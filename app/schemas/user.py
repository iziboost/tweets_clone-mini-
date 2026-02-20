from pydantic import BaseModel, ConfigDict


class UserShort(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    id: int
    name: str
    followers: list[UserShort]
    following: list[UserShort]
    model_config = ConfigDict(from_attributes=True)
