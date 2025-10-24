from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import credentials, messaging
import os

from app.utils.database import get_db
from app.models.models import AstrologerDetail

router = APIRouter()

# 🔥 Firebase Initialization
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # app/routers/
BASE_DIR = os.path.dirname(CURRENT_DIR)                  # app/
FIREBASE_PATH = os.path.join(BASE_DIR, "config", "firebase_astrologer.json")

print(f"Resolved Firebase path → {FIREBASE_PATH}")

if not os.path.exists(FIREBASE_PATH):
    raise FileNotFoundError(f"Firebase credentials file not found at {FIREBASE_PATH}")

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_PATH)
        firebase_admin.initialize_app(cred)
        print(f"Firebase initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
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
    """
    Register or update astrologer's FCM token in the database.
    """
    # --- Step 1: Fetch astrologer ---
    astrologer = db.query(AstrologerDetail).filter(
        AstrologerDetail.astro_id == data.astrologer_id,
        AstrologerDetail.isActive == True,
        AstrologerDetail.isDelete == False
    ).first()

    if not astrologer:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    if not data.fcm_token:
        raise HTTPException(status_code=400, detail="FCM token cannot be empty")

    # --- Step 2: Save token to DB ---
    try:
        astrologer.fcm_token = data.fcm_token
        db.commit()
        db.refresh(astrologer)
        print(f"FCM token saved for astrologer {astrologer.name}")
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error while saving token")

    return {"message": "Astrologer token saved successfully", "astrologer_id": astrologer.astro_id}


# 🔔 Send Notification to Astrologer
@router.post("/send-notification")
def send_astrologer_notification(data: SendAstroNotification, db: Session = Depends(get_db)):
    """
    Send push notification to astrologer using saved FCM token.
    """
    # --- Step 1: Fetch astrologer ---
    astrologer = db.query(AstrologerDetail).filter(
        AstrologerDetail.astro_id == data.astrologer_id,
        AstrologerDetail.isActive == True,
        AstrologerDetail.isDelete == False
    ).first()

    if not astrologer or not astrologer.fcm_token:
        raise HTTPException(status_code=404, detail="Astrologer or FCM token not found")

    # --- Step 2: Build Firebase message ---
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
        print(f"Notification sent to astrologer {astrologer.name} → Message ID: {response}")
        return {"message": "Notification sent successfully", "message_id": response}
    except Exception as e:
        import traceback
        print("Firebase send error:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to send notification")
