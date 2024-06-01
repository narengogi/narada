import sqlite3

con = sqlite3.connect('karani.db')
cur = con.cursor()

query = """
SELECT post_id, media FROM "main"."POSTS";
"""

# update_query = """
# UPDATE "main"."POSTS" set media =
# """

res = cur.execute(query)

for row in res.fetchall():
    post_id, media = row
    cur.execute(f"""UPDATE "main"."POSTS" set media = '{media}.jpg' where post_id = {post_id}""")
    con.commit()