from fastapi import APIRouter, HTTPException, Body
from app.core.database import supabase
from app.schemas.telemetry import TelemetryPayload

router = APIRouter(
    tags=["telemetry"],
)

@router.post("/ingest/{device_id}")
def ingest_data(device_id: str, payload: TelemetryPayload):
    # Verify device exists
    device = supabase.table("devices").select("device_id").eq("device_id", device_id).execute()
    if not device.data:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Insert telemetry
    # We store the Pydantic model as a dict in the JSONB column
    data = {
        "device_id": device_id,
        "payload": payload.model_dump(mode='json')
    }
    
    response = supabase.table("telemetry").insert(data).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to ingest data")
        
    return {"status": "success", "id": response.data[0]["id"]}
