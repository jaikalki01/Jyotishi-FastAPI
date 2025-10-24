from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import credentials, messaging
import os

from app.utils.database import get_db
from app.models.models import User  # ✅ Only User model is used for customers

router = APIRouter()

# 🔹 Firebase init
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIREBASE_PATH = os.path.join(BASE_DIR, "config/firebase_customer.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_PATH)
    firebase_admin.initialize_app(cred)
    print(f"🔥 Firebase connected successfully from {FIREBASE_PATH}")

# ✅ Pydantic model for FCM registration
class RegisterCustomerToken(BaseModel):
    user_id: str
    fcm_token: str

# ✅ Pydantic model for sending notification
class SendCustomerNotification(BaseModel):
    user_id: str
    title: str
    body: str

# ✅ Save/Update customer’s FCM token
@router.post("/register-token")
def register_customer_token(data: RegisterCustomerToken, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.fcm_token = data.fcm_token
    db.commit()
    return {"message": "Customer FCM token registered successfully"}

# ✅ Send notification to a customer
@router.post("/send-notification")
def send_customer_notification(data: SendCustomerNotification, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user or not user.fcm_token:
        raise HTTPException(status_code=404, detail="User FCM token not found")

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=data.title,
                body=data.body
            ),
            token=user.fcm_token
        )
        response = messaging.send(message)
        return {"message": "Notification sent successfully", "message_id": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
