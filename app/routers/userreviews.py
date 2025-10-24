from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.models import UserReview, User
from app.schemas.userreviews import (
    UserReviewCreate,
    UserReviewUpdate,
    UserReviewResponse,
)
from app.utils.database import get_db
from app.utils.authenticate import get_current_user  # ✅ Authentication import

router = APIRouter()

@router.post("/userreviews", response_model=UserReviewResponse)
def create_user_review(
    data: UserReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require auth
):
    review = UserReview(**data.dict())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/userreviews", response_model=List[UserReviewResponse])
def get_all_user_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require auth
):
    return db.query(UserReview).filter(UserReview.isDelete == False).all()


@router.get("/userreviews/{review_id}", response_model=UserReviewResponse)
def get_review_by_id(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require auth
):
    review = db.query(UserReview).filter_by(id=review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.put("/userreviews/{review_id}", response_model=UserReviewResponse)
def update_user_review(
    review_id: int,
    data: UserReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require auth
):
    review = db.query(UserReview).filter_by(id=review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(review, key, value)

    review.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(review)
    return review
