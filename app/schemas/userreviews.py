from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserReviewBase(BaseModel):
    userId: str
    rating: float = Field(..., ge=0, le=5)
    review: str
    astrologerId: Optional[str]
    reply: Optional[str]
    isActive: Optional[bool] = True
    isDelete: Optional[bool] = False
    isPublic: Optional[bool]
    createdBy: int
    modifiedBy: int


class UserReviewCreate(UserReviewBase):
    pass


class UserReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=0, le=5)
    review: Optional[str]
    reply: Optional[str]
    isActive: Optional[bool]
    isDelete: Optional[bool]
    isPublic: Optional[bool]
    modifiedBy: Optional[int]


class UserReviewResponse(UserReviewBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
