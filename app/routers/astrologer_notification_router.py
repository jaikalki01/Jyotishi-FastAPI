from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import credentials, messaging, exceptions
import os, re

from app.utils.database import get_db
from app.models.models import AstrologerDetail

router = APIRouter()

# 🔥 Firebase Initialization
# 🔥 Firebase Initialization (Windows-safe)


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # app/routers/
BASE_DIR = os.path.dirname(CURRENT_DIR)                       # app/
FIREBASE_PATH = os.path.join(BASE_DIR, "config", "firebase_astrologer.json")

# 🧠 Debug print — shows actual runtime path
print(f"Resolved Firebase path → {FIREBASE_PATH}")

if not os.path.exists(FIREBASE_PATH):
    raise FileNotFoundError(f"❌ Firebase credentials file not found at {FIREBASE_PATH}")

# 🔥 Initialize Firebase only once
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_PATH)
        firebase_admin.initialize_app(cred)
        print(f"🔥 Firebase connected successfully using {FIREBASE_PATH}")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        raise


# ✅ Pydantic Models
class RegisterAstroToken(BaseModel):
    astrologer_id: str
    fcm_token: str

class SendAstroNotification(BaseModel):
    astrologer_id: str
    title: str
    body: str


# 🟢 Register or Update Astrologer Token
@router.post("/register-token")
def register_astrologer_token(data: RegisterAstroToken, db: Session = Depends(get_db)):
    # --- Step 1: Basic validation ---
    if not data.fcm_token or len(data.fcm_token) < 100:
        raise HTTPException(status_code=400, detail="Invalid FCM token (too short)")

    if not re.match(r"^[\w-]{100,}$", data.fcm_token):
        raise HTTPException(status_code=400, detail="Malformed FCM token")

    # --- Step 2: Find astrologer ---
    astrologer = db.query(AstrologerDetail).filter(
        AstrologerDetail.astro_id == data.astrologer_id,
        AstrologerDetail.isActive == True,
        AstrologerDetail.isDelete == False
    ).first()

    if not astrologer:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    # --- Step 3: Validate token with Firebase ---
    try:
        messaging.send(messaging.Message(token=data.fcm_token), dry_run=True)
    except exceptions.FirebaseError as e:
        print(f"🔥 Firebase validation error: {e.code} - {e.message}")
        raise HTTPException(status_code=400, detail=f"Invalid FCM token: {e.message}")
    except Exception as e:
        print(f"🔥 Unexpected Firebase validation error: {e}")
        raise HTTPException(status_code=400, detail="Unable to verify FCM token")

    # --- Step 4: Save token to DB ---
    try:
        astrologer.fcm_token = data.fcm_token
        db.commit()
        db.refresh(astrologer)
    except Exception as e:
        db.rollback()
        print(f"❌ Database error while saving token: {e}")
        raise HTTPException(status_code=500, detail="Database error while saving token")

    return {
        "message": "Astrologer token saved successfully",
        "astrologer_id": astrologer.astro_id
    }


# 🔔 Send Notification to Astrologer
@router.post("/send-notification")
def send_astrologer_notification(data: SendAstroNotification, db: Session = Depends(get_db)):
    # --- Step 1: Fetch astrologer ---
    astrologer = db.query(AstrologerDetail).filter(
        AstrologerDetail.astro_id == data.astrologer_id,
        AstrologerDetail.isActive == True,
        AstrologerDetail.isDelete == False
    ).first()

    if not astrologer or not astrologer.fcm_token:
        raise HTTPException(status_code=404, detail="Astrologer or FCM token not found")

    # --- Step 2: Build message ---
    message = messaging.Message(
        notification=messaging.Notification(
            title=data.title,
            body=data.body
        ),
        token=astrologer.fcm_token
    )

    # --- Step 3: Send notification ---
    try:
        response = messaging.send(message)
        print(f"✅ Notification sent to astrologer ({astrologer.name}) → {response}")
        return {"message": "Notification sent successfully", "message_id": response}
    except exceptions.FirebaseError as e:
        print(f"🔥 Firebase Error [{e.code}]: {e.message}")
        raise HTTPException(status_code=400, detail=f"Firebase error: {e.message}")
    except Exception as e:
        print(f"🔥 Unexpected Firebase send error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")
