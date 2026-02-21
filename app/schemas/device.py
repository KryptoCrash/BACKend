from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeviceBase(BaseModel):
    device_id: str
    name: str

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True
