from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UpdateWalletRequest(BaseModel):
    balance: float

class WalletTransactionDetailResponse(BaseModel):
    id: int
    walletId: str
    amount: float
    transactionType: Optional[str]
    isCredit: bool
    status: Optional[str]
    from_user_id: Optional[str]
    to_user_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class WalletSendRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: float

class WalletSendResponse(BaseModel):
    message: str
    sender_wallet: dict
    receiver_wallet: dict



    class Config:
        orm_mode = True

class UpdateWalletRequest(BaseModel):
    amount: float


class UpdateWalletResponse(BaseModel):
    user_id: UUID
    balance: float   # frontend expects balance, backend stores in `amount`
    currency: str = "INR"


class WalletTransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: str = Field(alias="transactionType")  # 👈 map it    isCredit: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
