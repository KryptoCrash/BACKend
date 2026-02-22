from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DeviceBase(BaseModel):
    device_id: int
    name: str

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    device_id: int
    name: str
    owner_id: str