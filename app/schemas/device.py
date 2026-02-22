from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeviceBase(BaseModel):
    device_id: int
    name: str

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    owner_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
