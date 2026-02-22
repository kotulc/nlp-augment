from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List

from app.schemas.response import BaseResponse


class TagsEnum(str, Enum):
    entities = "entities"
    keywords = "keywords"
    related = "related"

class TagsRequest(BaseModel):
    content: str = Field(..., description="The text content to summarize")
    tags: List[TagsEnum] | None = Field(default_factory=List, description="The type of tags to extract")
    min_length: int | None = Field(default=1, description="The minimum length of related tags to extract")
    max_length: int | None = Field(default=3, description="The maximum length of related tags to extract")
    top_n: int | None = Field(default=10, description="The maximum number of strings to extract")

class TagsResults(BaseModel):
    tags: Dict[str, list] = Field(..., description="A list of extracted tags of each requested type")
    scores: Dict[str, list] = Field(..., description="A list of similarity scores for each tag type")

class TagsResponse(BaseResponse):
    results: TagsResults = Field(..., description="The result of the summary operation")
