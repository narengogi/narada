import json
import sqlite3
import os
from pathlib import Path
from typing import List

from utils import get_directory, escape_quotes

from instagrapi import Client

class Database():
    """
    This class handles database operations for the Instagram scraper.
    """

    def __init__(self, database_file: str) -> None:
        """
        Initialize a Database instance.

        This method establishes a connection to the SQLite database.

        Parameters:
        database_file (str): The name of the SQLite database file.

        Returns:
        None
        """
        self.db_connection = sqlite3.connect(database_file)
        self.cursor = self.db_connection.cursor()
        self.instagram_client = None 
    
    def insert_into_user_table(self, user: dict):
        """
        Insert a user into the USER table.

        This method inserts a user into the USER table of the SQLite database.

        Parameters:
        user (dict): A dictionary containing user information.

        Returns:
        None
        """
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

    #... other methods...

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
        database_file (str): The name of the SQLite database file.
        session_data (json): The session data for Instagram authentication.

        Returns:
        None
        """
        self.client = Client(session_data)
        self.database = Database(database_file)
        self.database.instagram_client = self.client
        self.posts = dict()

    #... other methods...

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
    friends = insta.get_friends(1)

    # For each friend, fetch their posts and limit to 5 posts
    for friend in friends:
        insta.get_user_posts(friend, 5)

if __name__ == '__main__':
    main()