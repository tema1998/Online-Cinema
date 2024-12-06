from typing import Generic, TypeVar, List, Optional

from fastapi import Query
from pydantic import BaseModel

# Create a type variable to allow PaginatedResponse to be generic
T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Query(1, description="Page number", gt=0)
    page_size: int = Query(
        10, description="Number of items per page", gt=0, le=100)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    total_pages: int
    prev: Optional[int]
    next: Optional[int]
    results: List[T]

    class Config:
        orm_mode = True
