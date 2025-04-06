from typing import List
from pydantic import BaseModel

class PaginatedResults(BaseModel):
    total: int
    results: List[BaseModel]

class MessageResponse(BaseModel):
    detail: str 