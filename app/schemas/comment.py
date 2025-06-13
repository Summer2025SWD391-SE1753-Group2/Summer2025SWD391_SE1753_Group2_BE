from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from datetime import datetime
from app.db.models.comment import CommentStatusEnum
from uuid import UUID

class AccountInfo(BaseModel):
    account_id: UUID4
    username: str
    full_name: str
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    post_id: UUID4
    parent_comment_id: Optional[UUID4] = None

class CommentCreate(CommentBase):
    pass  # account_id will be set automatically from authenticated user

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
    account: Optional[AccountInfo] = None
    replies: Optional[List['Comment']] = None

    class Config:
        from_attributes = True

class Comment(CommentInDBBase):
    pass

# Fix circular reference
Comment.model_rebuild() 