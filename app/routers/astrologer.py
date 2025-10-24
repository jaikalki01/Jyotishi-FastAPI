from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import time
import uuid
from app.models.models import AstrologerDetail, User, AstrologerAvailability
from app.schemas.astrologer import AstrologerDetailResponse
from app.utils.authenticate import get_current_user
from app.utils.database import get_db

router = APIRouter()

UPLOAD_DIR = Path("static/uploads/astrologers")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file(upload_file: UploadFile, dest_dir: Path) -> str:
    ext = Path(upload_file.filename).suffix or ""
    filename = f"{int(time.time()*1000)}_{uuid.uuid4().hex}{ext}"
    out_path = dest_dir / filename
    with out_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    try:
        upload_file.file.close()
    except:
        pass
    return str(out_path.resolve())


# ---------------- GET ALL ASTROLOGERS ----------------
@router.get("/astrologers", response_model=List[AstrologerDetailResponse])
def get_all_astrologers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    astrologers = db.query(AstrologerDetail).filter(AstrologerDetail.isDelete == False).all()

    response = []
    for astro in astrologers:
        response.append({
            "astro_id": astro.astro_id,
            "user_id": astro.user_id,
            "name": astro.name,
            "contactNo": astro.contactNo,
            "isContactVerified": astro.isContactVerified,
            "birthDate": astro.birthDate,
            "primarySkill": astro.primarySkill,
            "languageKnown": astro.languageKnown,
            "profileImage": astro.profileImage,
            "chatCharge": astro.chatCharge,
            "audioCallCharge": astro.audioCallCharge,
            "videoCallCharge": astro.videoCallCharge,
            "experienceInYears": astro.experienceInYears,
            "currentCity": astro.currentCity,
            "highestQualification": astro.highestQualification,
            "learnAstrology": astro.learnAstrology,
            "astrologerCategoryId": astro.astrologerCategoryId,
            "instaProfileLink": astro.instaProfileLink,
            "facebookProfileLink": astro.facebookProfileLink,
            "linkedInProfileLink": astro.linkedInProfileLink,
            "youtubeChannelLink": astro.youtubeChannelLink,
            "websiteProfileLink": astro.websiteProfileLink,
            "minimumEarning": astro.minimumEarning,
            "maximumEarning": astro.maximumEarning,
            "monthlyEarning": astro.monthlyEarning,
            "loginBio": astro.loginBio,
            "currentlyworkingfulltimejob": astro.currentlyworkingfulltimejob,
            "goodQuality": astro.goodQuality,
            "whatwillDo": astro.whatwillDo,
            "isVerified": astro.isVerified,
            "totalOrder": astro.totalOrder,
            "country": astro.country,
            "isActive": astro.isActive,
            "isDelete": astro.isDelete,
            "created_at": astro.created_at,
            "updated_at": astro.updated_at,
            "createdBy": str(astro.createdBy) if astro.createdBy is not None else None,
            "modifiedBy": str(astro.modifiedBy) if astro.modifiedBy is not None else None,
            "nameofplateform": astro.nameofplateform,
            "referedPerson": astro.referedPerson,
            "chatStatus": astro.chatStatus,
            "chatWaitTime": astro.chatWaitTime,
            "callStatus": astro.callStatus,
            "callWaitTime": astro.callWaitTime,
            "videoCallRate": astro.videoCallRate,
            "reportRate": astro.reportRate,
            "deleted_at": astro.deleted_at,
            "availabilitiesId": getattr(astro, "availabilitiesId", None)
        })

    return response


# ---------------- GET ASTROLOGER BY ID ----------------
@router.get("/astrologers/{astro_id}", response_model=AstrologerDetailResponse)
def get_astrologer_by_id(
    astro_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    astro = db.query(AstrologerDetail).filter(
        AstrologerDetail.astro_id == astro_id,
        AstrologerDetail.isDelete == False
    ).first()

    if not astro:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    return {
        "astro_id": astro.astro_id,
        "user_id": astro.user_id,
        "name": astro.name,
        "contactNo": astro.contactNo,
        "isContactVerified": astro.isContactVerified,
        "birthDate": astro.birthDate,
        "primarySkill": astro.primarySkill,
        "languageKnown": astro.languageKnown,
        "profileImage": astro.profileImage,
        "chatCharge": astro.chatCharge,
"audioCallCharge": astro.audioCallCharge,
"videoCallCharge": astro.videoCallCharge,
        "experienceInYears": astro.experienceInYears,
        "currentCity": astro.currentCity,
        "highestQualification": astro.highestQualification,
        "learnAstrology": astro.learnAstrology,
        "astrologerCategoryId": astro.astrologerCategoryId,
        "instaProfileLink": astro.instaProfileLink,
        "facebookProfileLink": astro.facebookProfileLink,
        "linkedInProfileLink": astro.linkedInProfileLink,
        "youtubeChannelLink": astro.youtubeChannelLink,
        "websiteProfileLink": astro.websiteProfileLink,
        "minimumEarning": astro.minimumEarning,
        "maximumEarning": astro.maximumEarning,
        "monthlyEarning": astro.monthlyEarning,
        "loginBio": astro.loginBio,
        "currentlyworkingfulltimejob": astro.currentlyworkingfulltimejob,
        "goodQuality": astro.goodQuality,
        "whatwillDo": astro.whatwillDo,
        "isVerified": astro.isVerified,
        "totalOrder": astro.totalOrder,
        "country": astro.country,
        "isActive": astro.isActive,
        "isDelete": astro.isDelete,
        "created_at": astro.created_at,
        "updated_at": astro.updated_at,
        "createdBy": str(astro.createdBy) if astro.createdBy is not None else None,
        "modifiedBy": str(astro.modifiedBy) if astro.modifiedBy is not None else None,
        "nameofplateform": astro.nameofplateform,
        "referedPerson": astro.referedPerson,
        "chatStatus": astro.chatStatus,
        "chatWaitTime": astro.chatWaitTime,
        "callStatus": astro.callStatus,
        "callWaitTime": astro.callWaitTime,
        "videoCallRate": astro.videoCallRate,
        "reportRate": astro.reportRate,
        "deleted_at": astro.deleted_at,
        "availabilitiesId": getattr(astro, "availabilitiesId", None)
    }



# ---------------- CREATE NEW ASTROLOGER ----------------



# ---------------- UPDATE ASTROLOGER ----------------
@router.put("/astrologers/{astrologer_id}", response_model=AstrologerDetailResponse)
def update_astrologer(
    astrologer_id: str,
    name: Optional[str] = Form(None),
    contactNo: Optional[str] = Form(None),
    primarySkill: Optional[str] = Form(None),
    languageKnown: Optional[str] = Form(None),
    chatCharge: Optional[float] = Form(None),
    audioCallCharge: Optional[float] = Form(None),
    videoCallCharge: Optional[float] = Form(None),
    experienceInYears: Optional[int] = Form(None),
    currentCity: Optional[str] = Form(None),
    profileImage: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Use the correct primary key attribute
    astrologer = db.query(AstrologerDetail).filter_by(astro_id=astrologer_id).first()
    if not astrologer:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    # ✅ Dynamic updates only for valid attributes
    allowed_fields = {
        "name", "contactNo", "primarySkill", "languageKnown",
        "chatCharge", "audioCallCharge", "videoCallCharge",
        "experienceInYears", "currentCity"
    }
    for key in allowed_fields:
        value = locals().get(key)
        if value is not None:
            setattr(astrologer, key, value)

    # ✅ Handle profile image upload
    if profileImage:
        saved_abs = save_upload_file(profileImage, UPLOAD_DIR)
        astrologer.profileImage = f"/static/uploads/astrologers/{Path(saved_abs).name}"

    # Optional: ensure modifiedBy is always a string to prevent ResponseValidationError
    astrologer.modifiedBy = str(current_user.id) if current_user.id is not None else None

    db.commit()
    db.refresh(astrologer)
    return astrologer

