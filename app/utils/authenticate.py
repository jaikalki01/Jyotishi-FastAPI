import hashlib
from datetime import datetime, timedelta
import requests
import pytz
from app.models.models import AstrologerDetail, User

from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.models.models import User, CustomerDetail
from app.utils.database import get_db

# India timezone
india_tz = pytz.timezone('Asia/Kolkata')

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT config
SECRET_KEY = "youggigigi867564secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days

# OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ------------------------
# Password utils
# ------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ------------------------
# JWT utils
# ------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")
    except JWTError:
        raise credentials_exception

    user = get_user(db, email=username)
    if user is None:
        raise credentials_exception

    return user


def check_user_role(required_role: int):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Access denied. Insufficient permissions")
        return user
    return role_checker


# ------------------------
# User utils
# ------------------------
def get_user(db: Session, email: str = None, contact: str = None, country_code: str = None):
    if email:
        return db.query(User).filter(User.email == email).first()

    if contact and country_code:
        user = db.query(User).join(CustomerDetail).filter(
            User.contactNo == contact,
            CustomerDetail.countryCode == country_code
        ).first()
        if user:
            return user
        return db.query(User).filter(User.contactNo == contact).first()

    return None


def authenticate_user(db: Session, username: str, password: str):
    if "@" in username:
        user = get_user(db=db, email=username)
    elif "-" in username:  # e.g. +91-8454078187
        country_code, contact = username.split("-")
        user = get_user(db=db, contact=contact, country_code=country_code)
    else:
        return None

    if not user or not verify_password(password, user.password):
        return None
    return user


# ------------------------
# Astrologer utils
# ------------------------
def authenticate_astro(db: Session, username: str, password: str):
    if "@" in username:
        astro = db.query(User).filter(User.email == username, User.role == "astrologer").first()
    else:
        astro = db.query(User).filter(User.contactNo == username, User.role == "astrologer").first()

    if not astro or not verify_password(password, astro.password):
        return None
    return astro


def get_astro(db: Session, contact: str, country_code: str):
    return db.query(User).filter(
        User.contactNo == contact,
        User.countryCode == country_code,
        User.role == "astrologer"
    ).first()


# ------------------------
# OTP utils
# ------------------------
def send_otp_whatsapp(mobile: str, otp: str) -> bool:
    url = "http://148.251.129.118/wapp/api/send"
    payload = {
        "apikey": "c26b5da4b3e9485cbf3413df31080450",
        "mobile": mobile,
        "msg": f"Your OTP for mobile application Umeed App is {otp} - Umeed App"
    }
    response = requests.get(url, params=payload)
    return response.status_code == 200


def send_otp_sms(mobile: str, otp: str) -> bool:
    # Ensure pure number (no + sign)
    clean_mobile = mobile.replace("+", "")

    if clean_mobile.startswith("91"):  # India
        url = "http://sms.messageindia.in/v2/sendSMS"
        payload = {
            "username": "sameerji",
            "message": f"Your OTP for mobile application jyotishionline login is {otp} jyotishi online",
            "sendername": "JYTSHI",
            "smstype": "TRANS",
            "numbers": clean_mobile,  # use stripped number
            "apikey": "242d4043-4734-4ae8-acb6-bcbb5b855bcc",
            "peid": "1701175032658751812",
            "templateid": "1707175048832142304"
        }
    else:
        url = "http://148.251.129.118/wapp/api/send"
        payload = {
            "apikey": "c26b5da4b3e9485cbf3413df31080450",
            "mobile": clean_mobile,
            "msg": f"Your OTP for mobile application Umeed App is {otp} Umeed App"
        }

    response = requests.get(url, params=payload)
    print("OTP SMS Response:", response.status_code, response.text)  # Debug log
    return response.status_code == 200

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_astrologer(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Extract the astrologer from JWT token.
    """
    payload = decode_access_token(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    astrologer = (
        db.query(AstrologerDetail)
        .join(User)
        .filter(User.email == user_email)
        .first()
    )
    if not astrologer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as astrologer")

    return astrologer