from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserDeviceDetailBase(BaseModel):
    appId: str
    deviceId: Optional[str]
    fcmToken: Optional[str]
    deviceLocation: Optional[str]
    deviceManufacturer: Optional[str]
    deviceModel: Optional[str]
    appVersion: Optional[str]
    isActive: Optional[bool] = True
    isDelete: Optional[bool] = False


class UserDeviceDetailCreate(UserDeviceDetailBase):
    id: str  # same as user id


class UserDeviceDetailUpdate(BaseModel):
    appId: Optional[str]
    deviceId: Optional[str]
    fcmToken: Optional[str]
    deviceLocation: Optional[str]
    deviceManufacturer: Optional[str]
    deviceModel: Optional[str]
    appVersion: Optional[str]
    isActive: Optional[bool]
    isDelete: Optional[bool]


class UserDeviceDetailResponse(UserDeviceDetailBase):
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
