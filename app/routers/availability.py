from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.models.models import AstrologerAvailability, User
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse
)
from app.utils.database import get_db
from app.utils.authenticate import get_current_user

router = APIRouter()


@router.post("/availabilities", response_model=AvailabilityResponse)
def create_availability(
    data: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    availability = AstrologerAvailability(
        **data.dict(),
        isDelete=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(availability)
    db.commit()
    db.refresh(availability)
    return availability


@router.get("/availabilities/{astrologer_id}", response_model=List[AvailabilityResponse])
def get_availabilities(
    astrologer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    availabilities = db.query(AstrologerAvailability).filter_by(
        astrologerId=astrologer_id,
        isDelete=False
    ).all()
    return availabilities


@router.get("/availability/{availability_id}", response_model=AvailabilityResponse)
def get_availability_by_id(
    availability_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    availability = db.query(AstrologerAvailability).filter_by(id=availability_id, isDelete=False).first()
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    return availability


@router.put("/availability/{availability_id}", response_model=AvailabilityResponse)
def update_availability(
    availability_id: int,
    data: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    availability = db.query(AstrologerAvailability).filter_by(id=availability_id, isDelete=False).first()
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(availability, key, value)

    availability.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(availability)
    return availability
