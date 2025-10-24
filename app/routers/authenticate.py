import random
import uuid

from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session

from app.models.models import AstrologerDetail, User
from app.utils.database import get_db
from app.utils.authenticate import (
    create_access_token,
    authenticate_user,
    authenticate_astro,
    get_user,
    get_astro,
    send_otp_whatsapp,
    send_otp_sms, verify_password,
)

router = APIRouter()

# OTP memory store (replace with Redis or DB in production)
otp_store = {}
OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 3

# ------------------------
# Normal user login
# ------------------------
@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": user}


# ------------------------
# Send OTP (user)
# ------------------------
@router.post("/send-otp")
def send_otp(
    contactNo: str = Form(...),
    countryCode: str = Form(...),
    send_whatsapp: bool = Form(True),
    send_sms: bool = Form(True),
):
    full_mobile = countryCode + contactNo
    otp = str(random.randint(100000, 999999))
    otp_store[full_mobile] = otp

    whatsapp_sent = send_otp_whatsapp(full_mobile, otp) if send_whatsapp else False
    sms_sent = send_otp_sms(full_mobile, otp) if send_sms else False

    if not whatsapp_sent and not sms_sent:
        raise HTTPException(status_code=500, detail="OTP send failed")

    return {"message": "OTP sent successfully"}


# ------------------------
# Verify OTP (user)
# ------------------------
@router.post("/verify-otp")
def verify_otp(contactNo: str = Form(...), countryCode: str = Form(...), otp: str = Form(...), db: Session = Depends(get_db)):
    full_mobile = countryCode + contactNo
    stored_otp = otp_store.get(full_mobile)

    if not stored_otp or stored_otp != otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = get_user(db, contact=contactNo, country_code=countryCode)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_store.pop(full_mobile, None)  # clear OTP
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "contactNo": user.contactNo}}


# ------------------------
# Astrologer login with OTP
from fastapi import BackgroundTasks

@router.post("/astro-login")
def astro_login(
    contactNo: str = Form(...),
    countryCode: str = Form(...),
    send_whatsapp: bool = Form(False),
    send_sms: bool = Form(True),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    full_mobile = countryCode if countryCode.startswith('+') else '+' + countryCode
    full_mobile += contactNo

    astro = get_astro(db, contact=contactNo, country_code=countryCode)
    if not astro:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    otp = str(random.randint(100000, 999999))
    otp_store[full_mobile] = otp

    def send_otp():
        if send_whatsapp:
            send_otp_whatsapp(full_mobile, otp)
        if send_sms:
            send_otp_sms(full_mobile, otp)

    # Run OTP sending in background
    background_tasks.add_task(send_otp)

    return {
        "message": "OTP requested, you should receive it shortly",
        "contactNo": contactNo,
        "countryCode": countryCode
    }



# ------------------------
# Verify OTP (Astrologer)
# ------------------------
@router.post("/astro-verify-otp")
def astro_verify_otp(
    contactNo: str = Form(...),
    countryCode: str = Form(...),
    otp: str = Form(...),
    db: Session = Depends(get_db)
):
    # Normalize full mobile number for OTP key
    full_mobile = countryCode if countryCode.startswith('+') else '+' + countryCode
    full_mobile += contactNo

    # OTP check
    stored_otp = otp_store.get(full_mobile)
    if not stored_otp or stored_otp != otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Get astro user
    astro = get_astro(db, contact=contactNo, country_code=countryCode)
    if not astro:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    # Get or create astrologer details
    astro_detail = astro.astrologer_detail  # if relationship is set up
    if not astro_detail:
        astro_detail = AstrologerDetail(
            astro_id=str(uuid.uuid4()),     # generate astro_id
            user_id=astro.id,               # link to user
            contactNo=astro.contactNo,
            countryCode=astro.countryCode,
            name=None,
            profileImage=None
        )
        db.add(astro_detail)
        db.commit()
        db.refresh(astro_detail)

    # Remove OTP after success
    otp_store.pop(full_mobile, None)

    # Create access token using user_id (or contactNo if that's your strategy)
    access_token = create_access_token(data={"sub": str(astro.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "astro": {
            "user_id": astro.id,                     # users.id
            "astro_id": astro_detail.astro_id,       # astrologer_details.astro_id
            "contactNo": astro.contactNo,
            "countryCode": astro.countryCode
        }
    }



@router.post("/user-login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    # Check user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify password
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    access_token = create_access_token(data={"sub": user.email, "id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }