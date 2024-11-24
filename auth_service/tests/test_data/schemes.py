from dataclasses import dataclass

from multidict import CIMultiDictProxy


@dataclass
class Response:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int
