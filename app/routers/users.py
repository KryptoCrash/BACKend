from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from app.core.security import get_current_user
from app.core.database import supabase
from app.core.config import settings
from app.utils.scoring import calculate_score
from app.schemas.telemetry import TelemetryResponse
from supabase import create_client, Client

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Initialize admin client for fetching users
# Note: This requires SUPABASE_SERVICE_ROLE_KEY to be set in .env
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

@router.get("/data", response_model=List[TelemetryResponse])
def get_all_user_data(user = Depends(get_current_user)):
    # 1. Get all device IDs owned by the user
    devices_response = supabase.table("devices").select("device_id").eq("owner_id", user.id).execute()
    
    if not devices_response.data:
        return []
        
    device_ids = [d["device_id"] for d in devices_response.data]
    
    # 2. Fetch telemetry for all these devices
    response = supabase.table("telemetry").select("*").in_("device_id", device_ids).order("created_at", desc=True).execute()
    
    data = response.data
    
    # 3. Calculate score for each record
    result = []
    for record in data:
        # Use the utility function to calculate score for this single record
        # calculate_score expects a list of records
        score = calculate_score([record])
        
        # Add score to the record so it matches TelemetryResponse schema
        record["score"] = score
        result.append(record)
        
    return result

@router.get("/leaderboard")
def get_leaderboard(limit: int = Query(20, ge=1, le=100)):
    # 1. Fetch all devices using admin client (bypass RLS)
    devices_resp = supabase_admin.table("devices").select("device_id, owner_id").execute()
    if not devices_resp.data:
        return []
        
    # Map device_id to owner_id
    device_owner_map = {d["device_id"]: d["owner_id"] for d in devices_resp.data}
    
    # 2. Fetch all telemetry using admin client (bypass RLS)
    telemetry_resp = supabase_admin.table("telemetry").select("*").execute()
    
    # 3. Group telemetry by user
    user_telemetry: Dict[str, List[Any]] = {}
    
    for record in telemetry_resp.data:
        d_id = record.get("device_id")
        owner_id = device_owner_map.get(d_id)
        
        if owner_id:
            if owner_id not in user_telemetry:
                user_telemetry[owner_id] = []
            user_telemetry[owner_id].append(record)
    
    # 4. Fetch user details (email) using admin client
    # Note: supabase-py doesn't expose list_users directly on auth.admin easily in older versions,
    # but we can try to fetch users or just use the IDs if listing is restricted.
    # However, supabase-py v2+ supports admin.list_users()
    
    user_map = {}
    try:
        users_resp = supabase_admin.auth.admin.list_users()
        for u in users_resp:
            user_map[u.id] = u.email
    except Exception as e:
        print(f"Error fetching users: {e}")
            
    # 5. Calculate scores
    leaderboard = []
    for owner_id, records in user_telemetry.items():
        score = calculate_score(records)
        
        email = user_map.get(owner_id, "unknown@example.com")
        username = email.split("@")[0] if email else "unknown"
        
        leaderboard.append({
            "username": username,
            "score": score
        })
        
    # Sort by score descending
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    return leaderboard[:limit]
