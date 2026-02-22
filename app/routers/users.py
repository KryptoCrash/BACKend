from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.core.security import get_current_user
from app.core.database import supabase
from app.utils.scoring import calculate_score

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/data")
def get_all_user_data(user = Depends(get_current_user)):
    # 1. Get all device IDs owned by the user
    devices_response = supabase.table("devices").select("device_id").eq("owner_id", user.id).execute()
    
    if not devices_response.data:
        return []
        
    device_ids = [d["device_id"] for d in devices_response.data]
    
    # 2. Fetch telemetry for all these devices
    response = supabase.table("telemetry").select("*").in_("device_id", device_ids).order("created_at", desc=True).execute()
    
    return response.data

@router.get("/leaderboard")
def get_leaderboard():
    # Note: This operation might be heavy and depends on RLS policies allowing access to all data.
    # If using the anon key with strict RLS, this might only return the current user's data or nothing.
    # For a real production app, consider using a Service Role key or a dedicated Postgres View/RPC.
    
    # 1. Fetch all devices (to map device_id -> owner_id)
    # We select device_id and owner_id
    devices_resp = supabase.table("devices").select("device_id, owner_id").execute()
    if not devices_resp.data:
        return []
        
    # Map device_id to owner_id
    device_owner_map = {d["device_id"]: d["owner_id"] for d in devices_resp.data}
    all_device_ids = list(device_owner_map.keys())
    
    if not all_device_ids:
        return []

    # 2. Fetch all telemetry
    # In a real app, you wouldn't fetch ALL rows. You'd use a SQL aggregation.
    # But for this boilerplate, we'll fetch and process in Python.
    telemetry_resp = supabase.table("telemetry").select("*").execute()
    
    # 3. Group telemetry by user
    user_telemetry: Dict[str, List[Any]] = {}
    
    for record in telemetry_resp.data:
        d_id = record.get("device_id")
        owner_id = device_owner_map.get(d_id)
        
        if owner_id:
            if owner_id not in user_telemetry:
                user_telemetry[owner_id] = []
            user_telemetry[owner_id].append(record)
            
    # 4. Calculate scores
    leaderboard = []
    for owner_id, records in user_telemetry.items():
        score = calculate_score(records)
        leaderboard.append({
            "user_id": owner_id,
            "score": score,
            "record_count": len(records)
        })
        
    # Sort by score descending
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    return leaderboard
