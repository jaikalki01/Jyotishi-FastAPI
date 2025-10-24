# app/schemas/rating.py
from pydantic import BaseModel, Field
from datetime import datetime

class CreateRating(BaseModel):
    user_id: str
    astrologer_id: str
    rating: int = Field(..., ge=1, le=10),
    review: str | None = None

class RatingResponse(BaseModel):
    id: int
    user_id: str
    astrologer_id: str
    rating: float
    review: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
