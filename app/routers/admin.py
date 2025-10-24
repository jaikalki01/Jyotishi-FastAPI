from agora_token_builder.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee



from datetime import datetime
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.models import User, AgoraConfig, ChatRoom
from app.utils.authenticate import get_current_user
from app.utils.database import get_db


router = APIRouter(prefix="/agora", tags=["Chat & Video Calls"])

# ✅ ---------- Pydantic Schemas ----------
class AgoraConfigBase(BaseModel):
    app_id: str
    app_certificate: Optional[str] = None
    app_name: Optional[str] = None
    environment: Optional[str] = "prod"
    status: Optional[bool] = True

class AgoraConfigResponse(AgoraConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ✅ ---------- VIDEO TOKEN ----------
@router.get("/token/video")
async def generate_agora_video_token(
    other_user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate Agora video token for any user or astrologer"""

    if not other_user_id:
        raise HTTPException(status_code=404, detail="Target user not found")

    # ✅ Allow all users — remove paid membership restriction
    # Just check for valid user and active Agora config

    room = (
        db.query(ChatRoom)
        .filter(
            ((ChatRoom.participant_a == current_user.id) & (ChatRoom.participant_b == other_user_id))
            | ((ChatRoom.participant_a == other_user_id) & (ChatRoom.participant_b == current_user.id))
        )
        .first()
    )

    if not room:
        room = ChatRoom(participant_a=current_user.id, participant_b=other_user_id)
        db.add(room)
        db.commit()
        db.refresh(room)


    config = db.query(AgoraConfig).filter(AgoraConfig.status == True).first()
    if not config:
        raise HTTPException(status_code=404, detail="Active Agora configuration not found.")

    if not config.app_id or not config.app_certificate:
        raise HTTPException(status_code=400, detail="Agora credentials incomplete.")

    # Default session time (e.g., 15 minutes)
    expire_seconds = 15 * 60
    channel_name = f"{current_user.id}-{other_user_id}"
    privilege_expiry = int(time.time()) + expire_seconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        config.app_id,
        config.app_certificate,
        channel_name,
        str(current_user.id),
        Role_Attendee,
    privilege_expiry,
    )

    return {
        "video_token": token,
        "channelName": channel_name,
        "timer": expire_seconds,
        "user": current_user.id,
        "userType": "General",
        "appID": config.app_name,
    }


# ✅ ---------- VOICE TOKEN ----------
@router.get("/token/voice")
async def generate_agora_voice_token(
    other_user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate Agora voice token for any user or astrologer"""

    if not other_user_id:
        raise HTTPException(status_code=404, detail="Target user not found")
    room = (
        db.query(ChatRoom)
        .filter(
            ((ChatRoom.participant_a == current_user.id) & (ChatRoom.participant_b == other_user_id))
            | ((ChatRoom.participant_a == other_user_id) & (ChatRoom.participant_b == current_user.id))
        )
        .first()
    )

    if not room:
        room = ChatRoom(participant_a=current_user.id, participant_b=other_user_id)
        db.add(room)
        db.commit()
        db.refresh(room)

    config = db.query(AgoraConfig).filter(AgoraConfig.status == True).first()
    if not config:
        raise HTTPException(status_code=404, detail="Active Agora configuration not found.")

    expire_seconds = 15 * 60
    channel_name = f"{current_user.id}-{other_user_id}"
    privilege_expiry = int(time.time()) + expire_seconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        config.app_id,
        config.app_certificate,
        channel_name,
        str(current_user.id),
        Role_Attendee,
        privilege_expiry,
    )

    return {
        "voice_token": token,
        "channelName": channel_name,
        "timer": expire_seconds,
        "user": current_user.id,
        "userType": "General",
        "appID": config.app_name,
    }
