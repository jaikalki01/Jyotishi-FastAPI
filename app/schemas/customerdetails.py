# app/schemas/customerdetails.py (for Pydantic v2)
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


def to_camel(s: str) -> str:
    parts = s.split('_')
    return parts[0] + ''.join(p.title() for p in parts[1:])


class CustomerDetailBase(BaseModel):
    # Pydantic v2 config
    model_config = {
        "from_attributes": True,        # allow reading attributes from ORM objects
        "alias_generator": to_camel,    # convert snake_case -> camelCase for external clients
        "populate_by_name": True,       # allow population using field names
    }
    name: Optional[str] = None
    contactNo: Optional[str] = None
    birth_date: Optional[date] = None
    birth_time: Optional[str] = None
    profile: Optional[str] = None              # textual bio
    profile_image: Optional[str] = None        # filename stored in DB
    birth_place: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    location: Optional[str] = None
    pincode: Optional[int] = None
    gender: Optional[str] = None
    fcm_token: Optional[str] = None
    token: Optional[str] = None
    expiration_date: Optional[datetime] = None
    country_code: Optional[str] = None


class CustomerDetailCreate(CustomerDetailBase):
    pass


class CustomerDetailUpdate(CustomerDetailBase):
    pass


class CustomerDetailResponse(CustomerDetailBase):
    id: str
    is_active: Optional[bool] = None
    is_delete: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    profile_image_url: Optional[str] = None   # full URL for client convenience
