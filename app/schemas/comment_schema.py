from pydantic import BaseModel, Field
from uuid import UUID

class CommentSchema(BaseModel):
    id: UUID
    text: str = Field(..., min_length=1)

class ClassificationTagSchema(BaseModel):
    tag: str
    explanation: str

class ClassificationResultSchema(BaseModel):
    comment_id: UUID
    category: str
    confidence: float
    tags: list[ClassificationTagSchema] = []