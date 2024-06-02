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
    SELECT * FROM USER WHERE username LIKE '%{user_name}%' or full_name LIKE '%{user_name}%';
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
         JOIN LOCATIONS L on POSTS.location = L.id
         JOIN TAGGED_USERS TU on POSTS.post_id = TU.post_id
         JOIN USER UT on UT.id = TU.user_id
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

def get_users_from_keyword(keyword):
    conn = sqlite3.connect('karani.db')
    cursor = conn.cursor()
    query = f"""
        SELECT U.full_name, P.* from POSTS P JOIN USER U on U.id = P.user_id where P.analysis LIKE '%{keyword}%';
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    result_lines = []
    for row in rows:
        line = ', '.join(str(item) for item in row)
        result_lines.append(line)

    all_results = '\n'.join(result_lines)
    return all_results


# def get_matching_posts(time: str = "-7 days", user_id: str = None):
#     cursor = conn.cursor()
#     query = f"""
#     SELECT analysis, l.name
#     FROM POSTS JOIN main.LOCATIONS L on POSTS.location = L.id
#     and timestamp >= datetime('now', '{time}')
#     and user_id = '{user_id}';    """
#     cursor.execute(query)
#     rows = cursor.fetchall()
#
#     result_lines = []
#     for row in rows:
#         line = ', '.join(str(item) for item in row)
#         result_lines.append(line)
#
#     all_results = '\n'.join(result_lines)
#     return all_results


def summarize(big_string: str, query: str):
    res = summarize_agent.sessions.chat(
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
            "name": "get_users_from_keyword",
            "description": "Extracts the most important keyword from the query string and searches for that keyword in the analysis column of the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The query to be displayed to the user to get the input.",
                    },
                },
                "required": ["keyword"]
            }
        }
    },
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
    "After getting the user_id get the relevant posts for the user_id and time using get_matching_posts_with_tagged_users",
    "If a random question is provided, figure out the most appropriate keyword in the query and get the relevant posts and summarise the analyses by calling get_users_from_keyword"
]

summarize_agent = client.agents.create(
    name="Summarizer",
    about="Summarizes the provided text for the provided query",
    model="gpt-4o",
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
    model="gpt-4o",
    metadata={"name": "Question Answerer"},
    tools=TOOLS,
    instructions=INSTRUCTIONS
)

while True:
    session = client.sessions.create(
        agent_id=agent.id,
        situation="Answer the questions asked by the user",
        metadata={"agent": "Question Answerer"},
    )
    user_input = input("Good Afternoon good sir, would you like some tea?\n")
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
    print("\n\n")
