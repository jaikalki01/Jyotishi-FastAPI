from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.block import ReportRequest, ReportResponse, BlockResponse, BlockRequest
from app.utils.database import get_db
from app.models.models import User, AstrologerReport, BlockedAstrologer, AstrologerDetail
from app.utils.authenticate import get_current_user

router = APIRouter()

# Report an astrologer


# ✅ Report an astrologer using astro_id
@router.post("/report", response_model=ReportResponse)
def report_astrologer(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    astrologer = db.query(AstrologerDetail).filter(AstrologerDetail.astro_id == request.astrologerId).first()
    if not astrologer:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    report = AstrologerReport(
        customerId=current_user.id,
        astrologerId=request.astrologerId,  # ✅ using astro_id
        reason=request.reason,
        created_at=datetime.utcnow()
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


# ✅ Block an astrologer by astro_id
@router.post("/block", response_model=BlockResponse)
def block_astrologer(
    request: BlockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    astrologer = db.query(AstrologerDetail).filter(AstrologerDetail.astro_id == request.astrologerId).first()
    if not astrologer:
        raise HTTPException(status_code=404, detail="Astrologer not found")

    existing_block = db.query(BlockedAstrologer).filter_by(
        customerId=current_user.id,
        astrologerId=request.astrologerId
    ).first()

    if existing_block:
        existing_block.isBlocked = True
        db.commit()
        db.refresh(existing_block)
        return existing_block

    block = BlockedAstrologer(
        customerId=current_user.id,
        astrologerId=request.astrologerId,  # ✅ astro_id reference
        isBlocked=True,
        created_at=datetime.utcnow()
    )

    db.add(block)
    db.commit()
    db.refresh(block)
    return block


# ✅ Unblock astrologer by astro_id
@router.delete("/unblock/{astrologer_id}")
def unblock_astrologer(
    astrologer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    blocked = db.query(BlockedAstrologer).filter_by(
        customerId=current_user.id,
        astrologerId=astrologer_id
    ).first()

    if not blocked:
        raise HTTPException(status_code=404, detail="Astrologer not blocked")

    db.delete(blocked)
    db.commit()
    return {"message": "Astrologer unblocked successfully"}
