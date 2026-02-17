from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List
from uuid import UUID

from app.schemas.response import BaseResponse


class MetricsEnum(str, Enum):
    diction = "diction"
    genre = "genre"
    mode = "mode"
    tone = "tone"
    sentiment = "sentiment"
    polarity = "polarity"
    toxicity = "toxicity"   
    spam = "spam"

class MetricsRequest(BaseModel):
    section_id: UUID = Field(..., description="The section id to associate with the supplied content")
    content: str = Field(..., description="The text content to summarize")
    metrics: List[MetricsEnum] | None = Field(default=None, description="The type of metrics to compute")

class MetricsResults(BaseModel):
    labels: List[str] = Field(..., description="A list of metric labels")
    scores: List[float] = Field(..., description="A list of metric scores")

class MetricsResponse(BaseResponse):
    results: Dict[MetricsEnum, MetricsResults] = Field(..., description="The result of the metrics operation")
