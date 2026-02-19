from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserShort

class LikeInfo(BaseModel):
    user_id: int
    name: str

class FeedTweet(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: UserShort
    likes: List[LikeInfo]
    model_config = ConfigDict(from_attributes=True)

class CreateTweet(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None

class CreateTweetResponse(BaseModel):
    result: bool = True
    tweet_id: int