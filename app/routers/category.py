from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models.models import AstrologerCategory
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.utils.database import get_db
from app.utils.authenticate import get_current_user # ✅ IMPORT THIS

router = APIRouter()

@router.post("/categories", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ✅ AUTH REQUIRED
):
    category = AstrologerCategory(
        **data.dict(),
        isDelete=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ✅ AUTH REQUIRED
):
    return db.query(AstrologerCategory).filter_by(isDelete=False).all()


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category_by_id(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ✅ AUTH REQUIRED
):
    category = db.query(AstrologerCategory).filter_by(id=category_id, isDelete=False).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # ✅ AUTH REQUIRED
):
    category = db.query(AstrologerCategory).filter_by(id=category_id, isDelete=False).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(category, key, value)

    category.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(category)
    return category
