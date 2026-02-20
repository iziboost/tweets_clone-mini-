from pydantic import BaseModel, ConfigDict


class MediaResponse(BaseModel):
    id: int
    url: str

    model_config = ConfigDict(from_attributes=True)


class CreateMediaResponse(BaseModel):
    result: bool = True
    media_id: int
