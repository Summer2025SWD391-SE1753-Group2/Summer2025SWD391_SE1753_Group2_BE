from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from datetime import datetime
from app.db.models.comment import CommentStatusEnum
from uuid import UUID

class CommentBase(BaseModel):
    content: str
    post_id: UUID4
    parent_comment_id: Optional[UUID4] = None

class CommentCreate(CommentBase):
    account_id: UUID4 = Field(..., description="ID of the account creating the comment")

class CommentUpdate(BaseModel):
    content: str

class CommentStatusUpdate(BaseModel):
    status: CommentStatusEnum

class CommentInDBBase(CommentBase):
    comment_id: UUID4
    account_id: UUID4
    status: str
    created_at: datetime
    level: int
    parent_level: Optional[int] = None

    class Config:
        from_attributes = True

class Comment(CommentInDBBase):
    pass

# Fix circular reference
CommentInDBBase.model_rebuild() 