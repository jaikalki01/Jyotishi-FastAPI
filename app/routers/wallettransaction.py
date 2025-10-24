from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from datetime import timedelta

from app.models.models import WalletTransaction, AstrologerDetail, User
from app.utils.database import get_db

router = APIRouter()


def format_duration(duration_seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    td = timedelta(seconds=duration_seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


# ======================================================
# ✅ 1️⃣ Astrologer Transactions
# ======================================================
@router.get("/wallet/transactions/astrologer/{astro_id}")
def get_astrologer_transactions(astro_id: str, db: Session = Depends(get_db)):
    """Fetch all wallet transactions for an astrologer."""
    transactions = (
        db.query(WalletTransaction)
        .filter(WalletTransaction.to_user_id == astro_id)
        .order_by(WalletTransaction.created_at.desc())
        .all()
    )

    result = []
    for txn in transactions:
        # Determine user name (prefer stored user_name field)
        user_name = txn.user_name or "Unknown"
        user_type = "unknown"

        # If not stored, resolve dynamically
        if not txn.user_name:
            user = db.query(User).filter(User.id == txn.from_user_id).first()
            if user:
                user_name = user.name
                user_type = "user"
            else:
                astro = db.query(AstrologerDetail).filter(AstrologerDetail.astro_id == txn.from_user_id).first()
                if astro:
                    user_name = astro.name
                    user_type = "astrologer"

        # Duration (use DB value or calculate)
        if txn.duration:
            duration_str = txn.duration
        elif txn.transaction_type in ["chat", "audio_call", "video_call"]:
            duration_seconds = (txn.updated_at - txn.created_at).total_seconds() if txn.updated_at else 0
            duration_str = format_duration(duration_seconds)
        else:
            duration_str = "00:00:00"

        result.append({
            "id": txn.id,
            "date": txn.created_at,
            "amount": txn.amount,
            "transactionType": txn.transaction_type,
            "status": txn.status,
            "duration": duration_str,
            "userName": user_name,
            "isCredit": txn.is_credit
        })

    return result


# ======================================================
# ✅ 2️⃣ User Transactions
# ======================================================
@router.get("/wallettransactions/user/{user_id}")
def get_wallet_transactions(user_id: str, db: Session = Depends(get_db)):
    transactions = (
        db.query(WalletTransaction)
        .filter(
            or_(
                WalletTransaction.from_user_id == user_id,
                WalletTransaction.to_user_id == user_id
            )
        )
        .order_by(WalletTransaction.created_at.desc())
        .all()
    )

    result = []
    for tx in transactions:
        other_user_id = tx.to_user_id if tx.from_user_id == user_id else tx.from_user_id
        user_name = tx.user_name or "Unknown"

        # Determine if it's a call/chat/send_money etc.
        txn_type = tx.transaction_type or "unknown"

        # Duration
        if tx.duration:
            duration_str = tx.duration
        elif txn_type in ["chat", "audio_call", "video_call"]:
            duration_seconds = (tx.updated_at - tx.created_at).total_seconds() if tx.updated_at else 0
            duration_str = format_duration(duration_seconds)
        else:
            duration_str = "00:00:00"

        # Try to resolve the other user's name
        if not tx.user_name:
            from app.models.models import AstrologerDetail, User
            astro = db.query(AstrologerDetail).filter(AstrologerDetail.astro_id == other_user_id).first()
            if astro:
                user_name = astro.name
            else:
                user = db.query(User).filter(User.id == other_user_id).first()
                if user:
                    user_name = user.name

        result.append({
            "id": tx.id,
            "amount": tx.amount,
            "transactionType": tx.transaction_type, # 👈 Added: chat / audio_call / video_call / send_money
            "status": tx.status,
            "isCredit": tx.is_credit,
            "created_at": tx.created_at,
            "userName": user_name,
            "duration": duration_str
        })

    return result

