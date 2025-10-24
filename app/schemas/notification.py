from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True
