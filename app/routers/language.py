from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.models import Language, User
from app.schemas.language import LanguageCreate, LanguageUpdate, LanguageResponse
from app.utils.database import get_db
from app.utils.authenticate import get_current_user  # ✅ Import authentication

router = APIRouter()


@router.post("/languages", response_model=LanguageResponse)
def create_language(
    data: LanguageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    new_lang = Language(**data.dict())
    db.add(new_lang)
    db.commit()
    db.refresh(new_lang)
    return new_lang


@router.get("/languages", response_model=List[LanguageResponse])
def get_all_languages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    return db.query(Language).all()


@router.get("/languages/{language_id}", response_model=LanguageResponse)
def get_language(
    language_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    lang = db.query(Language).filter_by(id=language_id).first()
    if not lang:
        raise HTTPException(status_code=404, detail="Language not found")
    return lang


@router.put("/languages/{language_id}", response_model=LanguageResponse)
def update_language(
    language_id: int,
    data: LanguageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require login
):
    lang = db.query(Language).filter_by(id=language_id).first()
    if not lang:
        raise HTTPException(status_code=404, detail="Language not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(lang, key, value)
    lang.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(lang)
    return lang
