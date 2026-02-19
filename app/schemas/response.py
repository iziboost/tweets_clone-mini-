from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    result: bool = True
    data: T

class SimpleResult(BaseModel):
    result: bool = True