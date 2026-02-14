from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, Text, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, BYTEA

from datetime import datetime
from sqlmodel import Field, SQLModel

from app.schemas.tags import TagsEnum


class SectionTypeEnum(str, Enum):
    heading = "heading"
    paragraph = "paragraph"
    list = "list"
    table = "table"
    figure = "figure"

class Metric(SQLModel, table=True):
    __tablename__ = "metrics"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    section_id: UUID = Field(default=None, foreign_key="sections.id", index=True, nullable=True)
    content: str = Field(..., sa_column=Column(Text, nullable=False))
    name: str = Field(..., index=True, nullable=False)
    value: float = Field(..., nullable=False)
    recorded_at: datetime = Field(default_factory=datetime.now, sa_column=Column(DateTime(timezone=False), nullable=False))

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    name: str = Field(primary_key=True)
    category: TagsEnum = Field(..., sa_column=Column(String(64), nullable=False))

class SectionTag(SQLModel, table=True):
    __tablename__ = "section_tags"
    section_id: UUID = Field(foreign_key="sections.id", primary_key=True)
    tag_name: str = Field(foreign_key="tags.name", primary_key=True)
    relevance: float = Field(..., nullable=False)
    position: Optional[int] = Field(default=None, nullable=False)

class Section(SQLModel, table=True):
    __tablename__ = "sections"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="documents.id", index=True, nullable=False)
    content: str = Field(..., sa_column=Column(Text, nullable=False))
    type: SectionTypeEnum = Field(..., nullable=False)
    level: Optional[int] = Field(default=None)
    position: Optional[int] = Field(default=None)
    metrics: List[Metric] = Relationship(back_populates="sections")
    tags: List[Tag] = Relationship(back_populates="sections", link_model=SectionTag)

class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slug: str = Field(..., index=True, unique=True, nullable=False)
    markdown: str = Field(..., sa_column=Column(Text, nullable=False))
    content_hash: str = Field(..., sa_column=Column(String(64), nullable=False))
    frontmatter: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(DateTime(timezone=False), nullable=False))
    updated_at: datetime = Field(default_factory=datetime.now, sa_column=Column(DateTime(timezone=False), nullable=False))
    sections: List[Section] = Relationship(back_populates="document")
