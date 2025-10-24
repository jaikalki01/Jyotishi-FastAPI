import uuid
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app.models.models import CustomerDetail, User, UserWallet
from app.schemas.customerdetails import CustomerDetailResponse
from app.utils.database import get_db
from app.utils.authenticate import get_current_user

router = APIRouter()
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ----------------------------------------
# Utility: Build full URL for uploaded images
# ----------------------------------------
def build_image_url(request: Request, filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    base = str(request.base_url).rstrip("/")
    return f"{base}/static/uploads/{filename}"


# ----------------------------------------
# POST: Create new customer record
# ----------------------------------------
@router.post("/customerdetails", response_model=CustomerDetailResponse)
def create_customer_detail(
    request: Request,
    name: str = Form(...),
    contactNo: str = Form(...),
    birthDate: str = Form(...),
    birthTime: str = Form(...),
    profile: Optional[str] = Form(None),
    birthPlace: str = Form(...),
    addressLine1: str = Form(...),
    addressLine2: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    pincode: int = Form(...),
    gender: str = Form(...),
    fcm_token: Optional[str] = Form(None),
    token: Optional[str] = Form(None),
    expirationDate: Optional[str] = Form(None),
    countryCode: Optional[str] = Form(None),
    profile_pic: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Restrict creation to customer role only
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can create customer accounts")

    # Ensure unique contact number
    contact_norm = (contactNo or "").strip()
    if db.query(CustomerDetail).filter(CustomerDetail.contactNo == contact_norm).first():
        raise HTTPException(status_code=409, detail="Contact number already used")

    # Handle optional profile image upload
    profile_image_filename = None
    if profile_pic and profile_pic.filename:
        safe_name = f"{uuid.uuid4()}_{profile_pic.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)
        with open(file_path, "wb") as f:
            f.write(profile_pic.file.read())
        profile_image_filename = safe_name

    # Create customer record
    customer = CustomerDetail(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=name,
        contactNo=contact_norm,
        birthDate=birthDate,
        birthTime=birthTime,
        profile=profile,
        birthPlace=birthPlace,
        addressLine1=addressLine1,
        addressLine2=addressLine2,
        location=location,
        pincode=pincode,
        gender=gender,
        fcm_token=fcm_token,
        token=token,
        expirationDate=expirationDate,
        countryCode=countryCode,
        profile_image=profile_image_filename,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(customer)

    # Create wallet if not already present
    if not db.query(UserWallet).filter(UserWallet.user_id == current_user.id).first():
        wallet = UserWallet(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            amount=Decimal(0),
            isActive=True,
            isDelete=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(wallet)

    try:
        db.commit()
        db.refresh(customer)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {e}")

    resp = CustomerDetailResponse.from_orm(customer).model_dump(by_alias=True)
    resp["profileImageUrl"] = build_image_url(request, customer.profile_image)
    resp["user_id"] = current_user.id
    return resp


# ----------------------------------------
# GET: Fetch all customers (Admin Only)
# ----------------------------------------
@router.get("/customerdetails/all", response_model=List[CustomerDetailResponse])
def get_all_customers(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Allow only admin users
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view all customers")

    customers = db.query(CustomerDetail).filter(CustomerDetail.isDelete == False).all()
    result = []
    for c in customers:
        data = CustomerDetailResponse.from_orm(c).model_dump(by_alias=True)
        data["profileImageUrl"] = build_image_url(request, c.profile_image)
        data["user_id"] = c.user_id
        result.append(data)
    return result


# ----------------------------------------
# GET: Fetch customer by user_id
# ----------------------------------------
@router.get("/customerdetails/get-by-userid/{user_id}", response_model=CustomerDetailResponse)
def get_customer_by_userid(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch a customer's record using their associated user_id.
    Useful for admin or system checks.
    """
    customer = db.query(CustomerDetail).filter(
        CustomerDetail.user_id == user_id,
        CustomerDetail.isDelete == False
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    resp = CustomerDetailResponse.from_orm(customer).model_dump(by_alias=True)
    resp["profileImageUrl"] = build_image_url(request, customer.profile_image)
    resp["user_id"] = customer.user_id
    return resp


# ----------------------------------------
# GET: Fetch customer details for logged-in user (/me)
# ----------------------------------------
@router.get("/customerdetails/me", response_model=CustomerDetailResponse)
def get_my_customer_detail(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch the customer details for the currently logged-in user
    using their JWT token (no user_id required in the URL).
    """
    user_id = current_user.id
    customer = db.query(CustomerDetail).filter(
        CustomerDetail.user_id == user_id,
        CustomerDetail.isDelete == False
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    resp = CustomerDetailResponse.from_orm(customer).model_dump(by_alias=True)
    resp["profileImageUrl"] = build_image_url(request, customer.profile_image)
    resp["user_id"] = customer.user_id
    return resp
