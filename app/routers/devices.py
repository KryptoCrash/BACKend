from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.security import get_current_user
from app.core.database import supabase
from app.schemas.device import DeviceCreate, DeviceResponse
from datetime import datetime
router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create", response_model=DeviceResponse)
def create_device(device: DeviceCreate, user = Depends(get_current_user)):
    # Check if device already exists
    existing = supabase.table("devices").select("*").eq("device_id", device.device_id).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Device ID already registered")

    new_device = {
        "device_id": device.device_id,
        "name": device.name,
        "owner_id": user.id
    }
    
    response = supabase.table("devices").insert(new_device).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create device")
    
    return response.data[0]

@router.get("/list", response_model=List[DeviceResponse])
def list_devices(user = Depends(get_current_user)):
    response = supabase.table("devices").select("*").eq("owner_id", user.id).execute()
    return response.data

@router.delete("/delete/{device_id}")
def delete_device(device_id: str, user = Depends(get_current_user)):
    # Verify ownership
    device = supabase.table("devices").select("*").eq("device_id", device_id).eq("owner_id", user.id).execute()
    if not device.data:
        raise HTTPException(status_code=404, detail="Device not found or not owned by user")
        
    supabase.table("devices").delete().eq("device_id", device_id).execute()
    return {"message": "Device deleted successfully"}

@router.get("/get/{device_id}/data")
def get_device_data(device_id: str, user = Depends(get_current_user)):
    # Verify ownership
    device = supabase.table("devices").select("*").eq("device_id", device_id).eq("owner_id", user.id).execute()
    if not device.data:
        raise HTTPException(status_code=404, detail="Device not found or not owned by user")
        
    response = supabase.table("telemetry").select("*").eq("device_id", device_id).order("created_at", desc=True).execute()
    return response.data

@router.get("/get_all_data")
def get_all_user_data(user = Depends(get_current_user)):
    # 1. Get all device IDs owned by the user
    devices_response = supabase.table("devices").select("device_id").eq("owner_id", user.id).execute()
    
    if not devices_response.data:
        return []
        
    device_ids = [d["device_id"] for d in devices_response.data]
    
    # 2. Fetch telemetry for all these devices
    # Using the "in" filter to match any of the device IDs
    response = supabase.table("telemetry").select("*").in_("device_id", device_ids).order("created_at", desc=True).execute()
    
    return response.data
