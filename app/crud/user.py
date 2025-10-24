import re
import threading
import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, text, desc, cast, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.models import User, AstrologerDetail, CustomerDetail, UserWallet
from app.schemas.user_schemas import UserCreate
from app.utils.authenticate import hash_password

user_id_lock = threading.Lock()

def generate_sequential_user_id(db):
    prefix = "UD"
    # Skip the first two characters ("UD") and cast the rest to integer for proper sorting
    last_user = (
        db.query(User)
        .filter(User.id.like(f"{prefix}%"))
        .order_by(desc(cast(func.substr(User.id, len(prefix)+1), Integer)))
        .first()
    )

    if last_user:
        last_number = int(last_user.id[len(prefix):])
    else:
        last_number = 0

    next_number = last_number + 1
    return f"{prefix}{str(next_number).zfill(4)}"  # UD00000001

def paginate(query, page: int, limit: int):
    total = query.count()
    skip = (page - 1) * limit
    items = query.offset(skip).limit(limit).all()
    has_next = skip + limit < total
    return total, has_next, items

def create_user(db: Session, user: UserCreate):
    user_id = f"user_{uuid.uuid4().hex}"

    db_user = User(
        id=user_id,
        email=user.email,
        password=hash_password(user.password),
        contactNo=user.contactNo,
        countryCode=user.countryCode,
        name=user.name,
        gender=user.gender,
        role=user.role
    )
    db.add(db_user)
    db.flush()  # Ensure user_id is accessible

    # Create related detail
    if user.role == 2:
        db.add(AstrologerDetail(id=user_id, birthDate=None, charge=0, primarySkill=""))
    elif user.role == 1:
        db.add(CustomerDetail(id=user_id, birthDate=None, birthTime=None))

    # Create wallet
    db.add(UserWallet(
        id=user_id,
        amount=0.0,
        isActive=True,
        isDelete=False,

    ))

    db.commit()
    db.refresh(db_user)
    return db_user

