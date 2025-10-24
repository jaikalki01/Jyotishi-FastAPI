from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.models import UserDeviceDetail, User
from app.schemas.userdevicedetails import (
    UserDeviceDetailCreate,
    UserDeviceDetailUpdate,
    UserDeviceDetailResponse,
)
from app.utils.database import get_db
from app.utils.authenticate import get_current_user  # ✅ Import auth

router = APIRouter()


@router.post("/userdevicedetails", response_model=UserDeviceDetailResponse)
def create_device_detail(
    data: UserDeviceDetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    if db.query(UserDeviceDetail).filter_by(id=data.id).first():
        raise HTTPException(status_code=400, detail="Device detail already exists for this user")

    device_detail = UserDeviceDetail(**data.dict())
    db.add(device_detail)
    db.commit()
    db.refresh(device_detail)
    return device_detail


@router.get("/userdevicedetails", response_model=List[UserDeviceDetailResponse])
def get_all_device_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    return db.query(UserDeviceDetail).filter(UserDeviceDetail.isDelete == False).all()


@router.get("/userdevicedetails/{user_id}", response_model=UserDeviceDetailResponse)
def get_device_detail(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    detail = db.query(UserDeviceDetail).filter_by(id=user_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Device detail not found")
    return detail


@router.put("/userdevicedetails/{user_id}", response_model=UserDeviceDetailResponse)
def update_device_detail(
    user_id: str,
    data: UserDeviceDetailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    detail = db.query(UserDeviceDetail).filter_by(id=user_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Device detail not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(detail, key, value)

    detail.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(detail)
    return detail
