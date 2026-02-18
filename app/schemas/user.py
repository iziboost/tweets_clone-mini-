from pydantic import BaseModel
from pydantic import ConfigDict


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)
