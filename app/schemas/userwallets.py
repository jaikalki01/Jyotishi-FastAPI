from uuid import UUID

from pydantic import BaseModel, Field, PositiveFloat
from typing import Optional, Literal
from datetime import datetime

class UserWalletCreate(BaseModel):
    user_id: str
    amount: Optional[float] = 0.0
    isActive: Optional[bool] = True
    isDelete: Optional[bool] = False

class UserWalletResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    isActive: bool
    isDelete: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


    class Config:
        from_attributes = True

class TopUpRequest(BaseModel):
    amount: float

class SendMoneyRequest(BaseModel):
    user_id: str
    astrologer_id: str
    amount: float
    type: Optional[str] = "send_money"  # can be chat/audio_call/video_call/send_money


   # or alias if you want snake_case

class UpdateWalletRequest(BaseModel):
    amount: float
    transaction_type: str = Field(..., alias="transactionType")  # frontend sends "transactionType"

    class Config:
        allow_population_by_field_name = True


class WalletDetailResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    isActive: bool
    isDelete: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True