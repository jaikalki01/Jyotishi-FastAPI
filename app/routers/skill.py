from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.models import Skill, User
from app.schemas.skill import SkillCreate, SkillUpdate, SkillResponse
from app.utils.database import get_db
from app.utils.authenticate import get_current_user  # ✅ Import authentication

router = APIRouter()


@router.post("/skills", response_model=SkillResponse)
def create_skill(
    data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    if db.query(Skill).filter(Skill.name == data.name).first():
        raise HTTPException(status_code=400, detail="Skill name must be unique")

    skill = Skill(**data.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/skills", response_model=List[SkillResponse])
def get_all_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    return db.query(Skill).filter(Skill.isDelete == False).all()


@router.get("/skills/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    skill = db.query(Skill).filter_by(id=skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/skills/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: int,
    data: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    skill = db.query(Skill).filter_by(id=skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(skill, key, value)

    skill.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(skill)
    return skill
