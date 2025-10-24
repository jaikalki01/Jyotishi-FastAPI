from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    image: Optional[str] = None
    isActive: Optional[bool] = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None
    isActive: Optional[bool] = None
    updated_at: Optional[datetime] = None


class CategoryResponse(CategoryBase):
    id: int
    isDelete: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
