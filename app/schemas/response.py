from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    result: bool = True
    data: T


class SimpleResult(BaseModel):
    result: bool = True
