from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from uuid import UUID, uuid4


class StatusEnum(str, Enum):
    created = "created"
    updated = "updated"
    failed = "failed"

class BaseResponse(BaseModel):
    """A base response model for all API responses"""
    id: UUID = Field(default_factory=uuid4, description="The unique record identifier")
    content_hash: str | None = Field(default=None, description="The unique content hash identifier")
    created_at: datetime = Field(description="The record creation timestamp")
    updated_at: datetime = Field(description="The record update timestamp")
    status: StatusEnum = Field(description="The status of the operation and resulting record")
    results: dict = Field(default_factory=dict, description="The returned results of the operation")
