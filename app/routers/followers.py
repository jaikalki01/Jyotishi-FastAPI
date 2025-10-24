from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.utils.database import get_db
from app.utils.authenticate import get_current_user  # ✅ Auth import
from app.models.models import AstrologerFollower, User
from app.schemas.followers import FollowerCreate, FollowerResponse

router = APIRouter()


@router.post("/followers", response_model=FollowerResponse)
def follow_astrologer(
    data: FollowerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    existing = db.query(AstrologerFollower).filter_by(
        astrologerId=data.astrologerId,
        userId=data.userId
    ).first()

    if existing:
        if existing.isDelete:
            existing.isDelete = False
            existing.isActive = True
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(status_code=400, detail="Already following")

    follow = AstrologerFollower(
        astrologerId=data.astrologerId,
        userId=data.userId
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow


@router.delete("/followers", response_model=FollowerResponse)
def unfollow_astrologer(
    data: FollowerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    follow = db.query(AstrologerFollower).filter_by(
        astrologerId=data.astrologerId,
        userId=data.userId,
        isDelete=False
    ).first()

    if not follow:
        raise HTTPException(status_code=404, detail="Follow entry not found")

    follow.isDelete = True
    follow.isActive = False
    follow.updated_at = datetime.utcnow()
    db.commit()
    return follow


@router.get("/followers/astrologer/{astrologer_id}", response_model=List[FollowerResponse])
def get_astrologer_followers(
    astrologer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    return db.query(AstrologerFollower).filter_by(
        astrologerId=astrologer_id,
        isDelete=False
    ).all()


@router.get("/followers/user/{user_id}", response_model=List[FollowerResponse])
def get_user_following(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    return db.query(AstrologerFollower).filter_by(
        userId=user_id,
        isDelete=False
    ).all()
