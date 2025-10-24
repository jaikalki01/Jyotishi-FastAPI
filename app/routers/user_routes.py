import os
import secrets
import shutil
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List

import requests
from fastapi import APIRouter, HTTPException, Depends, Request, Form, UploadFile, File, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

from app.crud.user import create_user
from app.models.models import User, AstrologerDetail, AstrologerWallet
from app.routers.authenticate import otp_store
from app.schemas.astrologer import AstrologerDetailResponse, AstrologerSignupRequest
from app.schemas.user_schemas import UserResponse, UserCreate
from app.utils.authenticate import hash_password, get_current_user
from app.utils.database import get_db

router = APIRouter()
token="bbb51ae4a5563b43a4088f906ff6868f"

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(file: UploadFile, user_id: str, suffix: str = ""):
    if not file:
        return None

    # Generate secure filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{user_id}_{suffix}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)


ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from decimal import Decimal
import uuid, os, secrets

from app.models.models import User, AstrologerDetail, AstrologerWallet
from app.utils.database import get_db
# assuming you have this function

ALLOWED_EXT = [".jpg", ".jpeg", ".png"]
UPLOAD_DIR = "static/uploads"

router = APIRouter()


@router.post("/signup/astrologer")
async def signup_astrologer(
        contactNo: str = Form(...),
        countryCode: str = Form(...),
        name: str = Form(...),
        email: str = Form(None),
        password: str = Form(None),
        gender: str = Form(None),
        birthDate: str = Form(None),
        primarySkill: str = Form(None),
        languageKnown: str = Form(None),
        chatCharge: int = Form(0),
        audioCallCharge: int = Form(0),
        videoCallCharge: int = Form(0),
        experienceInYears: int = Form(0),
        currentCity: str = Form(None),
        highestQualification: str = Form(None),
        learnAstrology: str = Form(None),
        astrologerCategoryId: str = Form(None),
        profileImage: UploadFile = File(None),
        db: Session = Depends(get_db),
):
    # --- 1️⃣ Check if user already exists ---
    existing_user = db.query(User).filter(
        (User.contactNo == contactNo) | (User.email == email)
    ).first()

    if existing_user:
        # If user is already a customer, block astrologer signup
        if existing_user.role == "customer":
            raise HTTPException(
                status_code=403,
                detail="Cannot create an astrologer account for a customer"
            )
        # If user is already an astrologer, block duplicate
        elif existing_user.role == "astrologer":
            raise HTTPException(
                status_code=400,
                detail="Astrologer account already exists for this user"
            )
        # Otherwise, you could upgrade them here if needed

    # --- 2️⃣ Create new user ---
    user_id = str(uuid.uuid4())
    generated_email = email or f"{contactNo}@jyotishi.com"
    generated_password = hash_password(password or secrets.token_hex(8))

    new_user = User(
        id=user_id,
        contactNo=contactNo,
        countryCode=countryCode,
        email=generated_email,
        password=generated_password,
        role="astrologer",
        lastSeen=datetime.utcnow(),
        unread_count=0,
        is_online=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # --- 3️⃣ Handle profile image ---
    saved_path = None
    if profileImage:
        ext = os.path.splitext(profileImage.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        unique_name = f"{user_id}_{int(datetime.utcnow().timestamp())}_{secrets.token_hex(6)}{ext}"
        disk_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(disk_path, "wb") as f:
            f.write(await profileImage.read())
        saved_path = f"/{disk_path.replace(os.sep, '/')}"

    # --- 4️⃣ Create AstrologerDetail ---
    astro = AstrologerDetail(
        user_id=user_id,
        name=name,
        contactNo=contactNo,
        isContactVerified=False,
        birthDate=birthDate,
        primarySkill=primarySkill,
        languageKnown=languageKnown,
        profileImage=saved_path,
        chatCharge=chatCharge,
        audioCallCharge=audioCallCharge,
        videoCallCharge=videoCallCharge,
        experienceInYears=experienceInYears,
        currentCity=currentCity,
        highestQualification=highestQualification,
        learnAstrology=learnAstrology,
        astrologerCategoryId=astrologerCategoryId,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(astro)
    db.commit()
    db.refresh(astro)

    # --- 5️⃣ Create Wallet ---
    new_wallet = AstrologerWallet(
        id=str(uuid.uuid4()),
        astrologer_id=astro.astro_id,
        amount=Decimal(0),
        isActive=True,
        isDelete=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)

    return {
        "message": "Astrologer registered successfully",
        "user_id": new_user.id,
        "astrologer_id": astro.astro_id,
        "wallet_id": new_wallet.id,
        "profile_image_url": astro.profileImage
    }
