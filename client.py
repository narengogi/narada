from julep import Client
import sqlite3
import json

from julep.api import ChatResponse

api_key = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODE3NzM3Ni1hZWQzLTQ4ZmMtYTc2MC1lOTY2ZGZlYThjNGIiLCJlbWFpbCI6Im5hcmVucm9ja3N0YXIxQGdtYWlsLmNvbSIsImlhdCI6MTcxNzI1NDEzNywiZXhwaXJlc0luIjoiMXkiLCJyYXRlTGltaXRQZXJNaW51dGUiOjM1MDAsInF1b3RhUmVzZXQiOiIxaCIsImNsaWVudEVudmlyb25tZW50Ijoic2VydmVyIiwic2VydmVyRW52aXJvbm1lbnQiOiJwcm9kdWN0aW9uIiwidmVyc2lvbiI6InYwLjIiLCJleHAiOjE3NDg4MTE3Mzd9.WKOUWvtTYnhVUFUcziKWXqyhIUs1jMH5ewBg_V_eEaJnFw5BELT8wx2wZnnRk11n1FCSO6AmCfMt9qaIb8b_6A"
client = Client(api_key=api_key)
conn = sqlite3.connect('karani.db')


def get_matching_users(user_name: str):
    connec = sqlite3.connect('karani.db')
    cursor = connec.cursor()
    query = f"""
    SELECT * FROM "main"."USER" WHERE username LIKE '%{user_name}%';
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    result_lines = []
    for row in rows:
        line = ', '.join(str(item) for item in row)
        result_lines.append(line)

    all_results = '\n'.join(result_lines)
    connec.close()
    return all_results


def get_matching_posts_with_tagged_users(user_id: str, time: str = "-7 days"):
    connec = sqlite3.connect('karani.db')
    cursor = connec.cursor()
    query = f"""
    SELECT 'analysis: ' || analysis, 'at: ' || l.name, 'alongwith: ' || UT.full_name as friends
    FROM POSTS
         JOIN main.LOCATIONS L on POSTS.location = L.id
         JOIN main.TAGGED_USERS TU on POSTS.post_id = TU.post_id
        JOIN main.USER UT on TU.user_id = POSTS.user_id
    and timestamp >= datetime('now', '{time}')
    and POSTS.user_id = '{user_id}';    """
    cursor.execute(query)
    rows = cursor.fetchall()

    result_lines = []
    for row in rows:
        line = ', '.join(str(item) for item in row)
        result_lines.append(line)

    all_results = '\n'.join(result_lines)
    connec.close()
    return all_results


def get_matching_posts(time: str = "-7 days", user_id: str = None):
    cursor = conn.cursor()
    query = f"""
    SELECT analysis, l.name
    FROM POSTS JOIN main.LOCATIONS L on POSTS.location = L.id
    and timestamp >= datetime('now', '{time}')
    and user_id = '{user_id}';    """
    cursor.execute(query)
    rows = cursor.fetchall()

    result_lines = []
    for row in rows:
        line = ', '.join(str(item) for item in row)
        result_lines.append(line)

    all_results = '\n'.join(result_lines)
    return all_results


def summarize(big_string: str, query: str):
    res = sumarize_agent.sessions.chat(
        session_id=summarize_session.id,
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": big_string
                    }
                ],
            }
        ],
        remember=False
    )
    return res.response[0][0].content


def take_user_input(query: str):
    return input(query)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "take_user_input",
            "description": "Takes a user input for the provided query and returns it as a string. It should be used to get user input for further processing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to be displayed to the user to get the input.",
                    },
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize",
            "description": "Summarizes the provided big string to a smaller string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "big_string": {
                        "type": "string",
                        "description": "The big string to be summarized.",
                    },
                    "query": {
                        "type": "string",
                        "description": "The query to be used to summarize the big string.",
                    },
                },
                "required": ["big_string", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_matching_users",
            "description": "Gets the users matching the provided user name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_name": {
                        "type": "string",
                        "description": "The user name to be used to get the matching users.",
                    },
                },
                "required": ["user_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_matching_posts",
            "description": "Gets the posts matching the provided time and user id. To get matching users you can invoke get_matching_users",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "The time to be used to get the matching posts. This is sqlite date comparator like '-7 days.'",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The user id to be used to get the matching posts.",
                    },
                },
                "required": ["time", "user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_matching_posts_with_tagged_users",
            "description": "Gets the matching posts alongwith tagged users matching the provided user id and time. Use it when you want to see who the user is tagging in their posts, or hanging out with.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user id to be used to get the tagged users.",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time to be used to get the tagged users. This is sqlite date comparator like '-7 days.'",
                    },
                },
                "required": ["user_id", "time"]
            }
        }
    }
]

INSTRUCTIONS = [
    "If you want to get user_id for a user name, invoke get_matching_users with the user name",
]

summarize_agent = client.agents.create(
    name="Summarizer",
    about="Summarizes the provided text for the provided query",
    model="gpt-3.5-turbo",
    metadata={"name": "Summarizer"}
)

summarize_session = client.sessions.create(
    agent_id=summarize_agent.id,
    situation="Analyse the provided images according to the requirements",
    metadata={"agent": "Instagram Post Analyser"},
)

agent = client.agents.create(
    name="Question Answerer",
    about="""
    Answers the questions asked by the user using the tools it has, if it requires more data, it will ask the user for it.
    Always invoke the summarize() tool at the end to summarize the data for the user.
    """,
    model="gpt-3.5-turbo",
    metadata={"name": "Question Answerer"},
    tools=TOOLS,
    instructions=INSTRUCTIONS
)

session = client.sessions.create(
    agent_id=agent.id,
    situation="Answer the questions asked by the user",
    metadata={"agent": "Question Answerer"},
)

while True:
    user_input = input("Good Afternoon good sir, what do you want to know about today?\n")
    if user_input == "exit":
        break
    outputs = []
    response = client.sessions.chat(
        session_id=session.id,
        messages=[
            {
                "role": "user",
                "content": user_input,
            }
        ],
    )
    while response.finish_reason == "tool_calls":
        for _responses in response.response:
            for _response in _responses:
                try:
                    tool_function = json.loads(_response.content)
                    args = json.loads(
                        tool_function.get("arguments", "{}")
                    )  # Parse the JSON string into a dictionary
                    tool = tool_function.get("name", "")
                    outputs.append(globals()[tool](**args))
                except json.JSONDecodeError:
                    outputs.append(_response.content)

        response = client.sessions.chat(  # submit the tool call
            session_id=session.id,
            messages=[
                {
                    "role": "assistant",
                    "content": json.dumps(outputs),
                }
            ],
            recall=True,
            remember=True,
        )
    print(response.response[0][0].content)
