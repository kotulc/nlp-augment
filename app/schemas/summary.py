from enum import Enum
from pydantic import BaseModel, Field
from typing import List

from app.schemas.response import BaseResponse


class SummaryEnum(str, Enum):
    title = "title"
    subtitle = "subtitle"
    description = "description"
    outline = "outline"

class SummaryRequest(BaseModel):
    content: str = Field(..., description="The text content to summarize")
    summary: SummaryEnum = Field(default="description", description="The type of summary to generate")
    top_n: int | None = Field(default=3, description="The number of summary items to generate")
    n_sections: int | None = Field(default=3, description="The number of sections for outline summaries")

class SummaryResults(BaseModel):
    summaries: List[str] = Field(..., description="A list of generated summaries of the requested type")
    scores: List[float] = Field(..., description="A list of similarity scores for each generated summary")

class SummaryResponse(BaseResponse):
    results: SummaryResults = Field(..., description="The result of the summary operation")
