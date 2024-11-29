from dataclasses import dataclass

from multidict import CIMultiDictProxy
from pydantic import BaseModel


@dataclass
class Response:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


class FilmSummary(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
