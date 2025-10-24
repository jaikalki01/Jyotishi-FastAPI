from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AvailabilityBase(BaseModel):
    astrologerId: str
    fromTime: Optional[str] = None
    toTime: Optional[str] = None
    day: str
    isActive: bool = True
    createdBy: int
    modifiedBy: int


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    fromTime: Optional[str] = None
    toTime: Optional[str] = None
    day: Optional[str] = None
    isActive: Optional[bool] = None
    modifiedBy: Optional[int] = None
    updated_at: Optional[datetime] = None


class AvailabilityResponse(AvailabilityBase):
    id: int
    isDelete: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
