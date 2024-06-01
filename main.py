from instagrapi import Client
import json
import sqlite3
from pathlib import Path

con = sqlite3.connect('karani.db')
cur = con.cursor()
cl = Client(json.load(open('session.json')))
# cl.login("naren.alt", "Saapa1@2")
# json.dump(
#     cl.get_settings(),
#     open('session.json', 'w')
# )
test = cl.account_info().dict()
account = cl.account_info()

# max_id = ""
# new_max_id = "123"
# user_list = []
# while True:
#     user_list, new_max_id = cl.user_following_v1_chunk(account.pk, 50, max_id)
#     # store user objects from here
#     if new_max_id == max_id:
#         break
#     max_id = new_max_id

following_dict = cl.user_following(account.pk, amount=10)

for user in following_dict.values():
    folder_path = Path('storage/' + user.username)
    if not folder_path.exists():
        folder_path.mkdir()
    profile_pic_path = str(folder_path) + '/profile_picture'
    cl.photo_download_by_url(user.profile_pic_url, 'profile_picture', folder_path)
    insert = f"""
    INSERT INTO "main"."USER" ("id", "name", "profile_pic", "username", "bio", "location_id")
     VALUES ('{str(user.pk)}', '{user.full_name}', '{profile_pic_path}', '{user.username}', '', '')
     ON CONFLICT(id) DO NOTHING;
    """
    cur.execute(insert)
    con.commit()
    posts = cl.user_medias_v1(user.pk, 20)
    for post in posts:
        if post.thumbnail_url is not None:
            image_path = str(cl.photo_download_by_url(post.thumbnail_url, str(post.pk), folder_path))
            insert = f"""
                            INSERT INTO "main"."POSTS" ("post_id", "media", "timestamp", "user_id")
                            VALUES ('{str(post.pk)}', '{image_path}', '{post.taken_at}', '{str(user.pk)}')
                            ON CONFLICT(post_id) DO NOTHING;
                        """
            cur.execute(insert)
            con.commit()
        else:
            for resource in post.resources:
                image_path = str(cl.photo_download_by_url(resource.thumbnail_url, str(resource.pk), folder_path))
                insert = f"""
                    INSERT INTO "main"."POSTS" ("post_id", "media", "timestamp", "user_id")
                    VALUES ('{str(resource.pk)}', '{image_path}', '{post.taken_at}', '{str(user.pk)}')
                    ON CONFLICT(post_id) DO NOTHING;
                """
                cur.execute(insert)
                con.commit()
    # end_cursor = ""
    # while True:
    #     new_posts, end_cursor = cl.user_medias_paginated(user.pk, amount=10, end_cursor=end_cursor)
    #     if not new_posts:
    #         break
    #     posts.append(new_posts)
    # store posts
