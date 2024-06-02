import json
import sqlite3
import os
from pathlib import Path
from typing import List
from models import User

from utils import get_directory, escape_quotes

from instagrapi import Client
from instagrapi.types import Location

class Database():
    def __init__(self, database_file: str) -> None:
        self.db_connection = sqlite3.connect(database_file)
        self.cursor = self.db_connection.cursor()
        self.instagram_client = None 
    
    def insert_into_user_table(self, user: dict):

        COMMAND = f"""
            INSERT INTO "main"."USER" 
            ("id", "username", "full_name", "bio", "profile_pic", "follower_count", "following_count")
            VALUES (
                '{str(user.get('pk'))}',
                '{user.get('username')}',
                '{escape_quotes(user.get('full_name'))}',
                '{escape_quotes(user.get('biography'))}',
                '{user.get('profile_pic')}',
                {user.get('follower_count')},
                {user.get('following_count')}
            )
            ON CONFLICT(id) DO NOTHING;
        """
        print(COMMAND)
        self.cursor.execute(COMMAND)
        self.db_connection.commit()

    def fetchall_from_user_table(self):
        COMMAND = f"""
            SELECT * FROM "main"."USER";
        """
        result = self.cursor.execute(COMMAND)
        return result

    def insert_into_location_table(self, location: Location):
        try:
            COMMAND = f"""
                INSERT INTO "main"."LOCATIONS" 
                ("id", "name", "address", "latitude", "longitude")
                VALUES (
                    '{str(location.pk)}',
                    '{escape_quotes(location.name)}',
                    '{escape_quotes(location.address)}',
                    {float(location.lat)},
                    {float(location.lng)}
                )
                ON CONFLICT(id) DO NOTHING;
            """
            print(COMMAND)
            self.cursor.execute(COMMAND)
            self.db_connection.commit()
            return location.pk
        except Exception as e:
            print("Skipping adding to location table due to issue: e")

    def insert_into_post_table(self, post):

        COMMAND = f"""
                    INSERT INTO "main"."POSTS" ("post_id", "timestamp", "location", "user_id", 
                    "like_count", "caption_text", "media", "title")
                    VALUES (
                        '{str(post.get("pk"))}', 
                        '{str(post.get("taken_at"))}', 
                        '{str(post.get("location"))}', 
                        '{str(post.get("user_pk"))}',
                        '{post.get("like_count")}',
                        '{escape_quotes(str(post.get("caption_text")))}',
                        '{str(post.get('media_path'))}',
                        '{escape_quotes(str(post.get('title')))}'
                    )
                        
                    ON CONFLICT(post_id) DO NOTHING;
                """
        print(COMMAND)
        self.cursor.execute(COMMAND)
        self.db_connection.commit()

    def delete(self, object):
        pass

    def update_user_table(self, pk, update_user):
        if pk != update_user.pk:
            raise Exception("User id does not match")
        
        COMMAND = f"""
            UPDATE "main"."USER" SET
                username = '{update_user.get('username')}',
                full_name = '{update_user.get('full_name')}',
                bio = '{update_user.get('biography')}',
            """

    def save_media(self, url, username, name, path = "storage/") -> Path:
        storage_path = get_directory(path, username)
        return str(self.instagram_client.photo_download_by_url(url, name, storage_path)).lstrip(str(os.getcwd()))


class Instagram():
    """
    This class implements an interface of Instagram using Instagrapi
    and stores data in a local SQLite DB to work with.
    """

    def __init__(self, database_file: str, session_data: json) -> None:
        """
        Initialize an Instagram instance.

        This method initializes an Instagrapi client for fetching data from Instagram
        It also establishes a connection to the SQLite database.

        Parameters:
        None

        Returns:
        None
        """
        self.client = Client(session_data)
        self.database = Database(database_file)
        self.database.instagram_client = self.client
        self.posts = dict()


    def get_friends(self, limit=0, from_database=False) -> List[dict]:
        """
        Get a list of friends.

        This method fetches a list of friends from Instagram.

        Parameters:
            count: int - Number of friends to retr
        Returns:
            List[User]
        """

        if from_database:
            response = self.database.fetchall_from_user_table()
            self.following = list()
            for row in response:
                self.following.append(User(**{k:v for k, v in zip(User.model_fields.keys(), list(row))}))
            return self.following
    
        account_info = self.client.account_info()
        users_following = self.client.user_following_v1(account_info.pk, amount=limit)
        for user_following in users_following:
            user = self.client.user_info(user_following.pk)
            dp_path = self.database.save_media(user.profile_pic_url_hd, user.username, "profile_picture")
            user = user.__dict__
            user.update({"profile_pic": dp_path})
            self.database.insert_into_user_table(user)

        return self.get_friends(from_database=True)

    
    def get_user_posts(self, user, limit=0):
        """
        Get a list of posts.

        This method fetches a list of posts from Instagram.

        Parameters:
            count: int - Number of posts to return
        Returns:
            List[Post]
        """

        posts = self.client.user_medias_v1(user.id, amount=limit)
        username = user.username
        self.posts[username] = list()
        for post in posts:
            try:
                media_path = str(self.database.save_media(post.thumbnail_url, username, post.pk))
            except Exception as e:
                media_path = f"ge/{username}/{post.pk}"

            
            for sno, resource in enumerate(post.resources):
                self.database.save_media(resource.thumbnail_url, username, f"{post.pk}_{sno}")

            if post.location:
                post.location = self.database.insert_into_location_table(post.location)
            else:
                post.location = None
            
            post.com
            post = post.__dict__
            post.update({"user_pk": user.id})
            post.update({"media_path": media_path})

            self.database.insert_into_post_table(post)

            self.posts[username].append(post)

        return self.posts[username]
            

def main():
    """
    Main function to run the Instagram scraper.

    This function initializes the Instagram scraper, fetches the friends list,
    and then fetches the posts for each friend.

    Parameters:
    None

    Returns:
    None
    """
    database_file = 'karani.db'  # Name of the SQLite database file
    session_data = None  # Placeholder for session data

    # Load session data from JSON file
    with open('session.json', 'r') as session:
        session_data = json.load(session)
    
    # Initialize Instagram scraper with database file and session data
    insta = Instagram(database_file, session_data)

    # Fetch friends list from Instagram and limit to 1 friend
    friends = insta.get_friends(from_database=True)

    # for friend in friends:
    #     insta.get_user_posts(friend, limit=5)
    #     print(friend)

    # For each friend, fetch their posts and limit to 5 posts
    for friend in friends[:30]:
        insta.get_user_posts(friend)

if __name__ == '__main__':
    main()