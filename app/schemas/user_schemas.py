from enum import Enum

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List, Union
from datetime import datetime, date


class UserBase(BaseModel):
    email: EmailStr
    name: str
    contactNo: Optional[str] = None
    countryCode: Optional[str] = None
    gender: Optional[str] = None
    role: int  # 1 = user, 2 = astrologer, 3 = admin

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: str

    class Config:
       orm_mode = True

class UserPublicResponse(BaseModel):
            id: str
            name: str
            gender: Optional[str] = None
            role: int  # 1 = user, 2 = astrologer, 3 = admin

            class Config:
               from_attributes = True
