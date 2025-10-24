# top of app/models/models.py — keep these imports only once
from datetime import datetime
from uuid import uuid4
import uuid
import random
import string
import pytz

from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text, Date, func, Index, Numeric, Enum
)
from sqlalchemy.orm import relationship, declarative_base, backref
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql.functions import current_user
from sqlalchemy.types import Enum as SQLEnum

from app.schemas.calls import SessionStatus, SessionType
from app.utils.database import get_db

india_tz = pytz.timezone('Asia/Kolkata')

Base = declarative_base()



ROLE_MAPPING = {
    'user': 1,
    'astrologer': 2,
    'admin': 3
}

def generate_prefixed_id(role: int) -> str:


    reverse_mapping = {v: k for k, v in ROLE_MAPPING.items()}
    prefix = {
        'user': "user",
        'astrologer': "astro",
        'admin': "admin"
    }.get(reverse_mapping.get(role, 'user'), "user")

    return f"{prefix}_{uuid.uuid4().hex}"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=True)
    password = Column(String(255))
    contactNo = Column(String(50))
    countryCode = Column(String(10))
    name = Column(String(100))
    gender = Column(String(50))
    role = Column(String(50), nullable=False)
    lastSeen = Column(DateTime, default=lambda: datetime.now(india_tz))
    unread_count = Column(Integer, default=0)
    is_online = Column(Boolean, default=False)

    session_requests = relationship("SessionRequest", back_populates="user", cascade="all, delete-orphan")  # ✅ points to user
    fcm_token = Column(String(255), nullable=True)

# --- relationships ---
    astrologer_detail = relationship(
        "AstrologerDetail",  # string name
        back_populates="user",
        foreign_keys="AstrologerDetail.user_id",  # string path
        uselist=False
    )
    customer_details = relationship(
        "CustomerDetail",
        back_populates="user",
        foreign_keys="CustomerDetail.user_id"
    )

    device_details = relationship(
        "UserDeviceDetail",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    sent_messages = relationship(
        "ChatMessage",
        foreign_keys="ChatMessage.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )

    received_messages = relationship(
        "ChatMessage",
        foreign_keys="ChatMessage.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
    wallets = relationship(
        "UserWallet",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class AstrologerDetail(Base):
    __tablename__ = "astrologer_details"

    # Primary ID for this table
    astro_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Unique astrologer ID (internal identifier, NOT FK)

    # Foreign key linking to users table
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Example astrologer-specific fields
    name = Column(String(255), nullable=False)
    contactNo = Column(String(20), unique=True, nullable=False)
    countryCode = Column(String(10), nullable=True)
    isContactVerified = Column(Boolean, default=False)
    otpCode = Column(String(10), nullable=True)
    otpExpiry = Column(DateTime, nullable=True)
    birthDate = Column(DateTime, nullable=True)
    primarySkill = Column(String(255), nullable=True)
    astrologerCategoryId = Column(String(50), ForeignKey("astrologer_categories.id"), nullable=True)
    languageKnown = Column(String(255), nullable=True)
    profileImage = Column(String(255))
    chatCharge = Column(Integer, default=0)
    audioCallCharge = Column(Integer, default=0)
    videoCallCharge = Column(Integer, default=0)
    experienceInYears = Column(Integer, nullable=True)
    currentCity = Column(String(255))
    highestQualification = Column(String(255), nullable=True)
    learnAstrology = Column(String(100))
    instaProfileLink = Column(String(255), nullable=True)
    facebookProfileLink = Column(String(255), nullable=True)
    linkedInProfileLink = Column(String(255), nullable=True)
    youtubeChannelLink = Column(String(255), nullable=True)
    websiteProfileLink = Column(String(255), nullable=True)
    minimumEarning = Column(Integer, nullable=True)
    maximumEarning = Column(Integer, nullable=True)
    monthlyEarning = Column(String(50), nullable=True)
    loginBio = Column(String(500), nullable=True)
    currentlyworkingfulltimejob = Column(String(255), nullable=True)
    goodQuality = Column(String(500), nullable=True)
    whatwillDo = Column(String(500), nullable=True)
    country = Column(String(100), nullable=True)
    createdBy = Column(String(50), nullable=True)
    modifiedBy = Column(String(50), nullable=True)
    nameofplateform = Column(String(255), nullable=True)
    referedPerson = Column(String(255), nullable=True)
    chatStatus = Column(String(50), nullable=True)
    chatWaitTime = Column(String(50), nullable=True)
    callStatus = Column(String(50), nullable=True)
    callWaitTime = Column(String(50), nullable=True)
    videoCallRate = Column(Integer, nullable=True)
    reportRate = Column(Integer, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    isVerified = Column(Boolean, default=False)
    totalOrder = Column(Integer, default=0)
    isActive = Column(Boolean, default=True)
    isDelete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz), onupdate=lambda: datetime.now(india_tz))
    isOnline = Column(Boolean, default=False)  # ✅ to show astrologer availability
    isBusy = Column(Boolean, default=False)  # ✅ to prevent multiple parallel sessions
    sessionType = Column(String(20), nullable=True)  # ✅ "chat" / "audio" / "video"
    currentPrice = Column(Float, nullable=True)
    session_requests = relationship("SessionRequest", back_populates="astrologer", cascade="all, delete-orphan")
    fcm_token = Column(String(255), nullable=True)


    # --- relationships ---
    user = relationship(
        "User",
        back_populates="astrologer_detail",
        foreign_keys=[user_id]
    )

    availabilities = relationship(
        "AstrologerAvailability",
        back_populates="astrologer",
        foreign_keys="AstrologerAvailability.astrologerId"
    )

    reviews = relationship(
        "UserReview",
        back_populates="astrologer",
        cascade="all, delete-orphan"
    )

    followers = relationship(
        "AstrologerFollower",
        back_populates="astrologer",
        cascade="all, delete-orphan"
    )

    blocked_users = relationship("BlockedAstrologer", back_populates="astrologer")


class CustomerDetail(Base):
    __tablename__ = "customer_details"

    id = Column(String(50), primary_key=True, index=True)  # customer record ID
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    contactNo = Column(String(20), unique=True, nullable=False)
    birthDate = Column(Date)
    birthTime = Column(String(50))
    profile = Column(String(255))
    profile_image = Column(String(400), nullable=True)
    birthPlace = Column(String(50))
    addressLine1 = Column(Text)
    addressLine2 = Column(Text)
    location = Column(String(100))
    pincode = Column(Integer)
    gender = Column(String(30))
    isActive = Column(Boolean, default=True)
    isDelete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    fcm_token = Column(String(400))
    token = Column(Text)
    expirationDate = Column(DateTime)
    countryCode = Column(String(45))
    deleted_at = Column(DateTime)

    # Correct relationship
    user = relationship(
        "User",
        back_populates="customer_details",
        foreign_keys=[user_id]
    )
    following = relationship("AstrologerFollower", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("UserReview", back_populates="customer", cascade="all, delete-orphan")





class AstrologerAvailability(Base):
    __tablename__ = "astrologer_availabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    astrologerId = Column(String(36), ForeignKey("astrologer_details.astro_id"), nullable=False)

    fromTime = Column(String(255))
    toTime = Column(String(255))
    day = Column(String(255), nullable=False)
    isActive = Column(Boolean, default=True, nullable=False)
    isDelete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    createdBy = Column(Integer, nullable=False)
    modifiedBy = Column(Integer, nullable=False)

    astrologer = relationship(
        "AstrologerDetail",
        back_populates="availabilities",
        foreign_keys=[astrologerId]
    )

# models.py — quick revert to legacy shape

# >>> in app/models/models.py (ensure this exact block exists)

# ... other imports ...

class UserWallet(Base):
    __tablename__ = "user_wallets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # wallet PK
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    wallet_id = Column(String(36), nullable=True)  # optional, if needed
    amount = Column(Float, default=0)
    isActive = Column(Boolean, default=True)
    isDelete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # relationship
    user = relationship("User", back_populates="wallets")


class WalletTransaction(Base):
    __tablename__ = "wallettransaction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(45), nullable=False)
    is_credit = Column(Boolean, nullable=False)
    status = Column(String(45), default="success")

    from_user_id = Column(String(50), nullable=True)  # supports UUID
    user_name = Column(String(150), nullable=True)    # store actual user/astro name

    to_user_id = Column(String(50), nullable=True)    # supports UUID
    duration = Column(String(20), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())





class AstrologerCategory(Base):
    __tablename__ = "astrologer_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    image = Column(String(255))
    isActive = Column(Boolean, default=True, nullable=False)
    isDelete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz))





class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    displayOrder = Column(Integer)
    isActive = Column(Boolean, default=True, nullable=False)
    isDelete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz))


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    languageName = Column(String(255), nullable=False)
    languageCode = Column(String(45))
    language_sign = Column(String(45))
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz))

class UserDeviceDetail(Base):
    __tablename__ = "user_device_details"

    id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    appId = Column(String(20), nullable=False)
    deviceId = Column(String(255))
    fcmToken = Column(String(255))
    deviceLocation = Column(String(255))
    deviceManufacturer = Column(String(255))
    deviceModel = Column(String(255))
    appVersion = Column(String(255))
    isActive = Column(Boolean, default=True)
    isDelete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    user = relationship("User", back_populates="device_details", passive_deletes=True)


class AstrologerWallet(Base):
    __tablename__ = "astrologer_wallets"

    # astrologer user id (FK to users.id)
    id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    astrologer_id = Column(String(36), ForeignKey("astrologer_details.astro_id"), nullable=False)

    # balance - using Float here to match existing pattern; prefer Numeric/Decimal for money in future
    amount = Column(Float, default=0.00, nullable=False)
    isActive = Column(Boolean, default=True, nullable=False)
    isDelete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz), onupdate=lambda: datetime.now(india_tz))

    # relationship back to user (optional)
    astrologer = relationship("User", backref="astrologer_wallet", foreign_keys=[id], passive_deletes=True)

class AstrologerFollower(Base):
    __tablename__ = "astrologer_followers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    astrologerId = Column(String(50), ForeignKey("astrologer_details.astro_id", ondelete="CASCADE"), nullable=False)
    userId = Column(String(50), ForeignKey("customer_details.id", ondelete="CASCADE"), nullable=False)

    isActive = Column(Boolean, default=True)
    isDelete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(india_tz))


    astrologer = relationship("AstrologerDetail", back_populates="followers")
    user = relationship("CustomerDetail", back_populates="following")






class UserReview(Base):
    __tablename__ = "user_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String(50), ForeignKey("customer_details.id"), nullable=False)
    rating = Column(Float(precision=2), nullable=False)
    review = Column(String(255), nullable=False)
    astrologerId = Column(String(36), ForeignKey("astrologer_details.astro_id"), nullable=True)  # ✅ fix here
    reply = Column(String(100), nullable=True)
    isActive = Column(Boolean, default=True)
    isDelete = Column(Boolean, default=False)
    isPublic = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=True, default=func.now())
    updated_at = Column(DateTime, nullable=True, default=func.now(), onupdate=func.now())
    createdBy = Column(Integer, nullable=False)
    modifiedBy = Column(Integer, nullable=False)

    # Relationships
    customer = relationship("CustomerDetail", back_populates="reviews")
    astrologer = relationship("AstrologerDetail", back_populates="reviews")


class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(String(80), primary_key=True, default=lambda: f"room_{uuid.uuid4().hex}")
    participant_a = Column(String(50), nullable=False)
    participant_b = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz))

    # ✅ per-room tracking
    unread_count_a = Column(Integer, default=0)
    unread_count_b = Column(Integer, default=0)
    last_seen_a = Column(DateTime, default=lambda: datetime.now(india_tz))
    last_seen_b = Column(DateTime, default=lambda: datetime.now(india_tz))

    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(80), ForeignKey("chat_rooms.id", ondelete="CASCADE"), index=True, nullable=False)
    sender_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    #metadata = Column(Text, nullable=True)  # optional JSON as string (attachments, type)
    meta_data = Column("metadata", Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(india_tz), index=True)
    is_read = Column(Boolean, default=False, nullable=False)  # read status for receiver

    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    # index for quick retrieval of latest messages per room
    __table_args__ = (
        Index("ix_chat_messages_room_created_at", "room_id", "created_at"),
    )


class AstrologerReport(Base):
    __tablename__ = "astrologer_reports"

    id = Column(String(50), primary_key=True, default=lambda: f"report_{uuid.uuid4().hex}")
    customerId = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    astrologerId = Column(String(36), ForeignKey("astrologer_details.astro_id", ondelete="CASCADE"), nullable=False)  # ✅ fix FK
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("User", foreign_keys=[customerId])
    astrologer = relationship("AstrologerDetail", foreign_keys=[astrologerId])  # ✅ fix relationship



class BlockedAstrologer(Base):
    __tablename__ = "blocked_astrologers"

    id = Column(String(100), primary_key=True, default=lambda: f"block_{uuid.uuid4().hex}")
    customerId = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    astrologerId = Column(String(100), ForeignKey("astrologer_details.astro_id", ondelete="CASCADE"), nullable=False)
    isBlocked = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
 # ✅ fixed class name


    customer = relationship("User", foreign_keys=[customerId])
    astrologer = relationship("AstrologerDetail", back_populates="blocked_users")

    # app/models/astrologer_request.py (or inside your models file)

    # --- Astrologer request enums & model (module-level) ---

    # --- Astrologer request enums & model (module-level) ---
    from enum import Enum as PyEnum  # keep one import at top of file

# --- Astrologer request enums & model (module-level) ---

class SessionRequest(Base):
    __tablename__ = "session_requests"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    astrologer_id = Column(String(100), ForeignKey("astrologer_details.astro_id", ondelete="CASCADE"), nullable=False)

    session_type = Column(Enum(SessionType), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.pending)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # relationships
    user = relationship("User", back_populates="session_requests")   # ✅ rename client → user
    astrologer = relationship("AstrologerDetail", back_populates="session_requests")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    astrologer_id = Column(String(100), nullable=False)

    rating = Column(Float, nullable=False)  # 1.0 - 5.0
    review = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AgoraConfig(Base):
    __tablename__ = "agora_configs"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String(255), nullable=False, unique=True)
    app_certificate = Column(String(255), nullable=True)
    app_name = Column(String(100), nullable=True)
    environment = Column(String(50), default="prod")  # dev/staging/prod
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())