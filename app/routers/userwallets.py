
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Body, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas.astrologer import AstrologerWalletResponse
from app.schemas.wallettransaction import WalletSendRequest, WalletSendResponse
from app.utils.authenticate import get_current_user
from app.utils.database import get_db
from app.models.models import UserWallet, WalletTransaction, User, AstrologerDetail,AstrologerWallet
from app.schemas.userwallets import (
    UserWalletCreate, UserWalletResponse, TopUpRequest, SendMoneyRequest, WalletDetailResponse, UpdateWalletRequest
)

router = APIRouter()


# --- Helper: get or create wallet ---



# --- 1. Create or Update Wallet ---
@router.post("/userwallets", response_model=UserWalletResponse)
def create_or_update_wallet(
    data: UserWalletCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # optional: admin only
):
    wallet = db.query(UserWallet).filter_by(user_id=data.user_id).first()

    if wallet:
        # Update existing wallet
        wallet.amount = data.amount
        wallet.isActive = data.isActive
        wallet.isDelete = data.isDelete
        wallet.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(wallet)
        return wallet

    # Create new wallet
    wallet = UserWallet(
        user_id=data.user_id,     # use the passed user ID
        amount=data.amount,
        isActive=data.isActive,
        isDelete=data.isDelete,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet



# --- 2. Top-up Wallet ---
@router.post("/wallet/top-up", response_model=UserWalletResponse)
def top_up_wallet(
    payload: TopUpRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Top-up amount must be positive")

    wallet = get_or_create_wallet(db, current_user.id)
    wallet.amount += payload.amount
    wallet.updated_at = datetime.utcnow()

    # Log transaction
    txn = WalletTransaction(
        walletId=wallet.id,
        amount=payload.amount,
        transactionType="top-up",
        status="success",
        isCredit=True,
        created_at=datetime.utcnow()
    )
    db.add(txn)
    db.commit()
    db.refresh(wallet)
    return wallet


@router.post("/send-money")
def send_money(
    request: SendMoneyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    """
    Transfer money from a user's wallet to an astrologer's wallet.
    Creates a WalletTransaction record with type info.
    """

    # 1️⃣ Validate user wallet
    user_wallet = db.query(UserWallet).filter(
        UserWallet.user_id == request.user_id,
        UserWallet.isActive == True,
        UserWallet.isDelete == False
    ).first()
    if not user_wallet:
        raise HTTPException(status_code=404, detail="User wallet not found")

    # 2️⃣ Check balance
    if user_wallet.amount < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # 3️⃣ Validate astrologer wallet
    astro_wallet = db.query(AstrologerWallet).filter(
        AstrologerWallet.astrologer_id == request.astrologer_id,
        AstrologerWallet.isActive == True,
        AstrologerWallet.isDelete == False
    ).first()
    if not astro_wallet:
        raise HTTPException(status_code=404, detail="Astrologer wallet not found")

    # 4️⃣ Perform transaction safely
    try:
        # Deduct and credit
        user_wallet.amount -= request.amount
        astro_wallet.amount += request.amount

        # Get related names
        user_obj = db.query(User).filter(User.id == request.user_id).first()
        astro_obj = db.query(AstrologerDetail).filter(AstrologerDetail.astro_id == request.astrologer_id).first()

        # 5️⃣ Record wallet transaction with type
        transaction = WalletTransaction(
            amount=request.amount,
            transaction_type=request.type,  # ✅ includes chat/audio/video/send_money
            is_credit=False,
            from_user_id=request.user_id,
            user_name=user_obj.name if user_obj else None,
            to_user_id=request.astrologer_id,
            duration="00:00:00",
            status="success",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return {
            "message": "Money sent successfully",
            "transaction_id": transaction.id,
            "transaction_type": request.type,
            "user_balance": user_wallet.amount,
            "astro_balance": astro_wallet.amount,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Get user ID by email
@router.get("/user/id/{email}")
def get_user_id(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "name": user.name}

# Get astrologer ID by phone number (contactNo)
@router.get("/astrologer/id/{phone}")
def get_astrologer_id(phone: str, db: Session = Depends(get_db)):
    astro = db.query(AstrologerDetail).filter(AstrologerDetail.contactNo == phone).first()
    if not astro:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    return {
        "id": astro.astro_id,  # <-- correct PK
        "name": astro.name,
        "phone": astro.contactNo
    }


@router.get("/userwallets/{user_id}", response_model=WalletDetailResponse)
def get_user_wallet(
    user_id: str,   # ✅ now accepts string IDs
    db: Session = Depends(get_db)
):
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return WalletDetailResponse(
        id=str(wallet.id),  # <-- must include
        user_id=wallet.user_id,
        amount=wallet.amount,
        isActive=wallet.isActive,
        isDelete=wallet.isDelete,
        created_at=wallet.created_at,
        updated_at=wallet.updated_at
    )


@router.put("/userwallets/{user_id}", response_model=WalletDetailResponse)
def update_wallet(
    user_id: str = Path(..., description="User ID"),
    data: UpdateWalletRequest = Body(...),  # <-- required body
    db: Session = Depends(get_db)
):
    # Fetch wallet
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Determine transaction type
    transaction_type = data.transaction_type.lower()
    if transaction_type == "credit":
        wallet.amount += data.amount
    elif transaction_type == "debit":
        if wallet.amount < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        wallet.amount -= data.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transactionType")

    # Update timestamp and commit
    wallet.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(wallet)

    # Return response
    return WalletDetailResponse(
        id=str(wallet.id),
        user_id=wallet.user_id,
        amount=wallet.amount,
        isActive=wallet.isActive,
        isDelete=wallet.isDelete,
        created_at=wallet.created_at,
        updated_at=wallet.updated_at
    )


@router.get("/astrowallet/{astro_id}", response_model=AstrologerWalletResponse)
def get_astrologer_wallet(
    astro_id: str,
    db: Session = Depends(get_db)
):
    wallet = db.query(AstrologerWallet).filter(AstrologerWallet.astrologer_id == astro_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Astrologer wallet not found")

    return AstrologerWalletResponse(
        id=str(wallet.astrologer_id),  # <-- matches schema field 'id'
        amount=wallet.amount,
        isActive=wallet.isActive,
        isDelete=wallet.isDelete,
        created_at=wallet.created_at,
        updated_at=wallet.updated_at
    )
