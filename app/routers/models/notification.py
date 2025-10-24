from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.utils.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)   # who will receive notification
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
