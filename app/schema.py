from pydantic import BaseModel, Field
from typing import Any, Dict, List


# Define general API request and response data models
class OperationRequest(BaseModel):
    id: int | None = Field(None, description="The id of the request record")
    content: str = Field(..., description="The text content for the requested operation")
    source: str | None = Field(None, description="A reference to the source from which the content was extracted")
    parameters: Dict[str, Any] | None = Field(default_factory=dict, description="Additional request parameters")

class OperationResponse(BaseModel):
    id: int | None = Field(None, description="The id of the returned record")
    success: bool = Field(True, description="The success status of the requested operation")
    result: Dict[str, Any] = Field(default_factory=dict, description="The results of the requested operation")
    metadata: Dict[str, Any] | None = Field(default_factory=dict, description="Metadata related to the operation")


# Define the generative data models (for testing and validation only)
class generativeRequest(BaseModel):
    content: str = Field(..., description="The text context used for generation")

class generativeResponse(BaseModel):
    results: List[str] = Field(None, description="The generated text content")


# Define the keyword extraction data models (for testing and validation only)
class keywordRequest(BaseModel):
    content: str = Field(..., description="The text to extract keywords from")

class keywordResponse(BaseModel):
    results: List[str] = Field(None, description="The extracted keyword and score pairs")


# Define the semantic data models (for testing and validation only)
class sentimentRequest(BaseModel):
    content: str = Field(..., description="The text context used for sentiment analysis")

class sentimentResponse(BaseModel):
    results: Dict[str, float] = Field(None, description="The sentiment label and score")


# Define the classifier data models (for testing and validation only)
class classifierRequest(BaseModel):
    content: str = Field(..., description="The text to classify")
    candidate_labels: List[str] = Field(..., description="The candidate labels to classify the text into")
    kwargs: dict = Field(None, description="Additional arguments for the classifier")

class classifierResponse(BaseModel):
    results: List[float] = Field(..., description="The classification scores for each candidate label")
