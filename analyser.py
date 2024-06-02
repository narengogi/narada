import sqlite3
import time

from julep import Client
import base64

con = sqlite3.connect('karani.db')
cur = con.cursor()

UNPROCESSED_ROWS = """
SELECT post_id, media FROM "main"."POSTS" WHERE analysis is null;
"""

api_key = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODE3NzM3Ni1hZWQzLTQ4ZmMtYTc2MC1lOTY2ZGZlYThjNGIiLCJlbWFpbCI6Im5hcmVucm9ja3N0YXIxQGdtYWlsLmNvbSIsImlhdCI6MTcxNzI1NDEzNywiZXhwaXJlc0luIjoiMXkiLCJyYXRlTGltaXRQZXJNaW51dGUiOjM1MDAsInF1b3RhUmVzZXQiOiIxaCIsImNsaWVudEVudmlyb25tZW50Ijoic2VydmVyIiwic2VydmVyRW52aXJvbm1lbnQiOiJwcm9kdWN0aW9uIiwidmVyc2lvbiI6InYwLjIiLCJleHAiOjE3NDg4MTE3Mzd9.WKOUWvtTYnhVUFUcziKWXqyhIUs1jMH5ewBg_V_eEaJnFw5BELT8wx2wZnnRk11n1FCSO6AmCfMt9qaIb8b_6A"
client = Client(api_key=api_key)

agent = client.agents.create(
    name="Instagram Post Analyser",
    about="Analyses instagram photos",
    model="gpt-4o",
    metadata={"name": "Instagram Post Analyser"},
)

session = client.sessions.create(
    agent_id=agent.id,
    situation="Analyse the provided images according to the requirements",
    metadata={"agent": "Instagram Post Analyser"},
)

prompt = """
Your task is to analyse the provided image and summarize the photo in less than 150 words:
1. If there are people in the photo, describe their emotions, actions, and interactions.
2. If there are objects in the photo, describe their appearance, location, and purpose.
3. If there are any text in the photo, describe its content and relevance.
4. If there are any animals in the photo, describe their species, actions, and interactions.
5. If there are any landmarks in the photo, describe their appearance, location, and significance.
6. If there are any other elements in the photo, describe their appearance, location, and relevance.
7. If the photo is a meme, describe its content, humor, and relevance.
8. If the photo is a screenshot, describe its content, context, and relevance.
9. If the photo is a selfie, describe the person's appearance, expression, and context.
10. If the photo is a landscape, describe the location, weather, and significance.
"""

res = cur.execute(UNPROCESSED_ROWS)

for row in res.fetchall():
    post_id, media = row
    if "." not in media.rsplit("/")[-1]:
        continue
    base64_image = base64.b64encode(open("/Users/narendranathchoudharygogineni/Documents/personal/narada/" + media, "rb").read()).decode("utf-8")
    res = client.sessions.chat(
        session_id=session.id,
        messages=[
            {
              "role": "system",
              "content": [
                  {
                      "type": "text",
                      "text": prompt
                  }
              ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    }
                ],
            }
        ],
        max_tokens=1024,
        remember=False
    )
    content = res.response[0][0].content.replace("```json", "")
    content = content.replace("```", "")
    content = content.replace("'", "")
    print(content)
    cur.execute(f"""UPDATE "main"."POSTS" set analysis = '{content}' where post_id = '{post_id}'""")
    con.commit()
    # time.sleep(1000)

