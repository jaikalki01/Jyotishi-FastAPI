from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class AstrologerDetailResponse(BaseModel):
    astro_id: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    contactNo: Optional[str] = None
    isContactVerified: Optional[bool] = None
    birthDate: Optional[datetime] = None
    primarySkill: Optional[str] = None
    languageKnown: Optional[str] = None
    profileImage: Optional[str] = None
    chatCharge: int
    audioCallCharge: int
    videoCallCharge: int
    experienceInYears: Optional[int] = None
    currentCity: Optional[str] = None
    highestQualification: Optional[str] = None
    learnAstrology: Optional[str] = None
    astrologerCategoryId: Optional[str] = None
    instaProfileLink: Optional[str] = None
    facebookProfileLink: Optional[str] = None
    linkedInProfileLink: Optional[str] = None
    youtubeChannelLink: Optional[str] = None
    websiteProfileLink: Optional[str] = None
    minimumEarning: Optional[int] = None
    maximumEarning: Optional[int] = None
    monthlyEarning: Optional[str] = None
    loginBio: Optional[str] = None
    currentlyworkingfulltimejob: Optional[str] = None
    goodQuality: Optional[str] = None
    whatwillDo: Optional[str] = None
    isVerified: Optional[bool] = None
    totalOrder: Optional[int] = None
    country: Optional[str] = None
    isActive: Optional[bool] = None
    isDelete: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    createdBy: Optional[str] = None  # allow string now
    modifiedBy: Optional[str] = None
    nameofplateform: Optional[str] = None
    referedPerson: Optional[str] = None
    chatStatus: Optional[str] = None
    chatWaitTime: Optional[str] = None
    callStatus: Optional[str] = None
    callWaitTime: Optional[str] = None
    videoCallRate: Optional[int] = None
    reportRate: Optional[int] = None
    deleted_at: Optional[datetime] = None
    availabilitiesId: Optional[int] = None

    class Config:
        orm_mode = True


class AstrologerDetailUpdate(BaseModel):
        availabilitiesId: Optional[int] = None
        birthDate: Optional[datetime] = None
        primarySkill: Optional[str] = None
        languageKnown: Optional[str] = None
        profileImage: Optional[str] = None
        charge: Optional[int] = None
        experienceInYears: Optional[int] = None
        currentCity: Optional[str] = None
        highestQualification: Optional[str] = None
        learnAstrology: Optional[str] = None
        astrologerCategoryId: Optional[str] = None
        instaProfileLink: Optional[str] = None
        facebookProfileLink: Optional[str] = None
        linkedInProfileLink: Optional[str] = None
        youtubeChannelLink: Optional[str] = None
        websiteProfileLink: Optional[str] = None
        minimumEarning: Optional[int] = None
        maximumEarning: Optional[int] = None
        loginBio: Optional[str] = None
        currentlyworkingfulltimejob: Optional[str] = None
        goodQuality: Optional[str] = None
        whatwillDo: Optional[str] = None
        isVerified: Optional[bool] = None
        totalOrder: Optional[int] = None
        country: Optional[str] = None
        isActive: Optional[bool] = None
        isDelete: Optional[bool] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None
        createdBy: Optional[int] = None
        modifiedBy: Optional[int] = None
        nameofplateform: Optional[str] = None
        monthlyEarning: Optional[str] = None
        referedPerson: Optional[str] = None
        chatStatus: Optional[str] = None
        chatWaitTime: Optional[str] = None
        callStatus: Optional[str] = None
        callWaitTime: Optional[str] = None
        videoCallRate: Optional[int] = None
        reportRate: Optional[int] = None
        deleted_at: Optional[datetime] = None


# app/schemas/astrologer.py


class AstrologerSignupRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    contactNo: str
    countryCode: str
    name: str
    gender: Optional[str] = None
    isContactVerified: Optional[bool] = False
    otpCode: Optional[str] = None
    otpExpiry: Optional[datetime] = None
    birthDate: Optional[datetime] = None
    primarySkill: Optional[str] = None
    languageKnown: Optional[str] = None
    profileImage: Optional[str] = None   # <-- here
    charge: Optional[int] = 0
    experienceInYears: Optional[int] = 0
    currentCity: Optional[str] = None
    highestQualification: Optional[str] = None
    learnAstrology: Optional[str] = None
    astrologerCategoryId: Optional[str] = None
    instaProfileLink: Optional[str] = None
    facebookProfileLink: Optional[str] = None
    linkedInProfileLink: Optional[str] = None
    youtubeChannelLink: Optional[str] = None
    websiteProfileLink: Optional[str] = None
    minimumEarning: Optional[int] = 0
    maximumEarning: Optional[int] = 0
    monthlyEarning: Optional[str] = None
    totalOrder: Optional[int] = 0
    currentlyworkingfulltimejob: Optional[str] = None
    nameofplateform: Optional[str] = None
    referedPerson: Optional[str] = None
    loginBio: Optional[str] = None
    goodQuality: Optional[str] = None
    whatwillDo: Optional[str] = None
    isVerified: Optional[bool] = False
    isActive: Optional[bool] = True
    isDelete: Optional[bool] = False
    chatStatus: Optional[str] = None
    chatWaitTime: Optional[str] = None
    callStatus: Optional[str] = None
    callWaitTime: Optional[str] = None
    videoCallRate: Optional[int] = 0
    reportRate: Optional[int] = 0
    createdBy: Optional[str] = None
    modifiedBy: Optional[str] = None


class AstrologerWalletCreate(BaseModel):
        # For creation/update payloads (client supplies amount and flags)
        amount: float = 0.0
        isActive: bool = True
        isDelete: bool = False

        model_config = ConfigDict(from_attributes=True)

class AstrologerWalletResponse(BaseModel):
        # Server -> client representation (include meta fields)
        id: str
        amount: float
        isActive: bool
        isDelete: bool
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None

        model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)