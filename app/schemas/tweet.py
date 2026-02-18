from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from pydantic import ConfigDict

from app.schemas.user import UserResponse
from app.schemas.media import MediaResponse


class CreateTweet(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None


class TweetResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: UserResponse
    medias: List[MediaResponse]

    model_config = ConfigDict(from_attributes=True)
