from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SkillBase(BaseModel):
    name: str
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = True
    isDelete: Optional[bool] = False


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None
    isDelete: Optional[bool] = None


class SkillResponse(SkillBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
