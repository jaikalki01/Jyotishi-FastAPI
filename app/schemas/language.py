from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LanguageBase(BaseModel):
    languageName: str
    languageCode: Optional[str] = None
    language_sign: Optional[str] = None


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    languageName: Optional[str] = None
    languageCode: Optional[str] = None
    language_sign: Optional[str] = None


class LanguageResponse(LanguageBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
