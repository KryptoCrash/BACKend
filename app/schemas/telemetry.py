from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TelemetryPayload(BaseModel):
    potentiometer_value: float = Field(..., description="Reading from the potentiometer sensor")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data or URL")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of reading")

class TelemetryCreate(BaseModel):
    payload: TelemetryPayload

class TelemetryResponse(BaseModel):
    telemetry_id: int
    device_id: int
    payload: TelemetryPayload
    created_at: Optional[datetime] = None
    score: float

    class Config:
        from_attributes = True
