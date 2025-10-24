from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class ChatMessageCreate(BaseModel):
    room_id: str
    sender_id: str
    receiver_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageOut(BaseModel):
    id: int
    room_id: str
    sender_id: str
    receiver_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageOut]
    page: int
    size: int
    total: int


class LastMessageOut(BaseModel):
    id: int
    room_id: str
    sender_id: str
    receiver_id: str
    content: str
    created_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}
