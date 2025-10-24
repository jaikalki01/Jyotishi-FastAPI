# app/routers/ratings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.models import Rating
from app.schemas.rating import CreateRating, RatingResponse

router = APIRouter()

# ✅ User rates an astrologer
@router.post("/", response_model=RatingResponse)
def create_rating(data: CreateRating, db: Session = Depends(get_db)):
    # Validate rating manually
    if not (1 <= data.rating <= 10):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 10")

    existing = db.query(Rating).filter(
        Rating.user_id == data.user_id,
        Rating.astrologer_id == data.astrologer_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already rated this astrologer")

    rating = Rating(
        user_id=data.user_id,
        astrologer_id=data.astrologer_id,
        rating=data.rating,
        review=data.review
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


# ✅ Get all ratings for an astrologer
@router.get("/astrologer/{astrologer_id}", response_model=list[RatingResponse])
def get_astrologer_ratings(astrologer_id: str, db: Session = Depends(get_db)):
    return db.query(Rating).filter(Rating.astrologer_id == astrologer_id).order_by(Rating.created_at.desc()).all()
