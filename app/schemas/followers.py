from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FollowerBase(BaseModel):
    astrologerId: str
    userId: str


class FollowerCreate(FollowerBase):
    pass


class FollowerResponse(FollowerBase):
    id: int
    isActive: bool
    isDelete: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
