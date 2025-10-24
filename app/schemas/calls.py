from pydantic import BaseModel
from datetime import datetime
from app.models.enums import SessionType, SessionStatus

class CreateSessionRequest(BaseModel):
    user_id: str
    astrologer_id: str
    session_type: SessionType

class SessionRequestResponse(BaseModel):
    id: int
    user_id: str
    astrologer_id: str
    session_type: SessionType
    status: SessionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UpdateSessionStatus(BaseModel):
    status: SessionStatus
