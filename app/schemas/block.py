from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportRequest(BaseModel):
    astrologerId: str
    reason: Optional[str] = None


class BlockRequest(BaseModel):
    astrologerId: str


class ReportResponse(BaseModel):
    id: str
    customerId: str
    astrologerId: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class BlockResponse(BaseModel):
    id: str
    customerId: str
    astrologerId: str
    isBlocked: bool
    created_at: datetime

    class Config:
        from_attributes = True
