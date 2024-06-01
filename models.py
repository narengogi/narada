from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    full_name: str
    bio: str
    profile_pic: str
    follower_count: int
    following_count: int