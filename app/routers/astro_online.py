from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.models import SessionRequest, AstrologerDetail, UserWallet, AstrologerWallet
from app.utils.database import get_db
from app.utils.authenticate import get_current_user
from app.models.enums import SessionType, SessionStatus

router = APIRouter()

@router.post("/start")
def start_session(
    astrologer_id: str,
    session_type: SessionType,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Start a new session (chat/audio/video).
    """
    astrologer = db.query(AstrologerDetail).filter(
        AstrologerDetail.astro_id == astrologer_id,
        AstrologerDetail.isActive == True,
        AstrologerDetail.isDelete == False
    ).first()

    if not astrologer:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    # Check if astrologer is busy
    active_session = db.query(SessionRequest).filter(
        SessionRequest.astrologer_id == astrologer_id,
        SessionRequest.status == SessionStatus.ongoing
    ).first()
    if active_session:
        raise HTTPException(status_code=400, detail="Astrologer is busy with another session")

    # Check user wallet balance
    wallet = db.query(UserWallet).filter(UserWallet.user_id == current_user.id).first()
    if not wallet or wallet.amount <= 0:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    new_session = SessionRequest(
        user_id=current_user.id,
        astrologer_id=astrologer_id,
        session_type=session_type,
        status=SessionStatus.ongoing,
        created_at=datetime.utcnow()
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "message": "Session started successfully",
        "session_id": new_session.id,
        "astrologer": astrologer.name,
        "sessionType": session_type,
        "start_time": new_session.created_at
    }


@router.post("/end/{session_id}")
def end_session(session_id: int, db: Session = Depends(get_db)):
    """
    End a session and deduct wallet amount based on astrologer’s fixed rate.
    """
    session = db.query(SessionRequest).filter(SessionRequest.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.ongoing:
        raise HTTPException(status_code=400, detail="Session already ended or invalid")

    astrologer = db.query(AstrologerDetail).filter(AstrologerDetail.astro_id == session.astrologer_id).first()
    user_wallet = db.query(UserWallet).filter(UserWallet.user_id == session.user_id).first()
    astro_wallet = db.query(AstrologerWallet).filter(AstrologerWallet.astrologer_id == session.astrologer_id).first()

    # Decide session price based on astrologer’s rate
    if session.session_type == SessionType.chat:
        charge = astrologer.chatCharge
    elif session.session_type == SessionType.audio_call:
        charge = astrologer.audioCallCharge
    elif session.session_type == SessionType.video_call:
        charge = astrologer.videoCallCharge
    else:
        charge = 0

    if user_wallet.amount < charge:
        raise HTTPException(status_code=400, detail="Insufficient balance to complete session")

    # Deduct and credit
    user_wallet.amount -= charge
    if astro_wallet:
        astro_wallet.amount += charge

    # Update session status
    session.status = SessionStatus.ended
    session.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Session ended successfully",
        "price_deducted": charge,
        "user_wallet_balance": user_wallet.amount
    }


@router.get("/astrologers/online")
def get_online_astrologers(db: Session = Depends(get_db)):
    astrologers = db.query(AstrologerDetail).filter(
        AstrologerDetail.isActive == True,
        AstrologerDetail.isDelete == False,
        AstrologerDetail.chatStatus == "online"  # or any online flag
    ).all()

    result = []
    for astro in astrologers:
        result.append({
            "id": astro.astro_id,
            "name": astro.name,
            "profileImage": astro.profileImage,
            "chatCharge": astro.chatCharge,
            "audioCallCharge": astro.audioCallCharge,
            "videoCallCharge": astro.videoCallCharge,
            "waitTime": astro.chatWaitTime or "15 min"
        })

    return result
