import sqlite3

con = sqlite3.connect('karani.db')
cur = con.cursor()

query = """
SELECT post_id, media FROM "main"."POSTS";
"""

# update_query = """
# UPDATE "main"."POSTS" set media =
# """

# res = cur.execute(query)
#
# for row in res.fetchall():
#     post_id, media = row
#     cur.execute(f"""UPDATE "main"."POSTS" set media = '{media}.jpg' where post_id = {post_id}""")
#     con.commit()
#
# tagged_users_query = """
# SELECT * FROM TAGGED_USERS;
# """
#
# res = cur.execute(tagged_users_query)
#
# for row in res.fetchall():
#     post_id, user_id = row
#     cur.execute(f"""UPDATE "main"."TAGGED_USERS" set user_id = (SELECT id FROM USER ORDER BY RANDOM() LIMIT 1) where post_id = {post_id}""")
#     con.commit()
# con.close()


res = cur.execute(query)

for row in res.fetchall():
    post_id, media = row
    cur.execute(f"""UPDATE POSTS set location = (SELECT id FROM LOCATIONS ORDER BY RANDOM() LIMIT 1) where post_id = {post_id}""")
    con.commit()

con.close()
