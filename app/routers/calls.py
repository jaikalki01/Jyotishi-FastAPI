from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.models import SessionRequest, SessionStatus
from app.schemas.calls import CreateSessionRequest, SessionRequestResponse, UpdateSessionStatus
from app.models.notification import Notification
from app.utils.ws_manager import manager
import asyncio

router = APIRouter()

# ✅ User creates a session request (chat/audio/video)
@router.post("/create", response_model=SessionRequestResponse)
def create_session_request(data: CreateSessionRequest, db: Session = Depends(get_db)):
    req = SessionRequest(
        user_id=data.user_id,
        astrologer_id=data.astrologer_id,
        session_type=data.session_type,
        status=SessionStatus.pending
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

# ✅ Astrologer fetches all pending requests
@router.get("/astrologer/{astrologer_id}", response_model=list[SessionRequestResponse])
def get_requests(astrologer_id: str, db: Session = Depends(get_db)):
    return (
        db.query(SessionRequest)
        .filter(SessionRequest.astrologer_id == astrologer_id)
        .order_by(SessionRequest.created_at.desc())
        .all()
    )

# ✅ Astrologer responds (accept/decline)
@router.patch("/{request_id}", response_model=SessionRequestResponse)
async def respond_request(
    request_id: int,
    data: UpdateSessionStatus,
    db: Session = Depends(get_db)
):
    request = db.query(SessionRequest).filter(SessionRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != SessionStatus.pending:
        raise HTTPException(status_code=400, detail="Request already responded")

    # update status
    request.status = data.status
    db.commit()
    db.refresh(request)

    # create notification for user
    msg = f"Your {request.session_type.value} request was {request.status.value} by astrologer."
    notification = Notification(user_id=request.user_id, message=msg)
    db.add(notification)
    db.commit()

    # ✅ now you can await safely
    await manager.send_personal_message(request.user_id, msg)

    return request
