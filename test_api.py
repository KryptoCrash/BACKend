import os
import requests
import json
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_URL = "http://127.0.0.1:8000"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

# Initialize Supabase client for authentication
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_auth_token():
    email = "kryptocrashmh@gmail.com"
    password = "testpassword123"
    
    print(f"Authenticating as {email}...")
    
    try:
        # Try to sign in
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print("Signed in successfully.")
        return response.session.access_token
    except Exception as e:
        print(f"Sign in failed: {e}")
        try:
            # Try to sign up if sign in fails
            print("Attempting to sign up...")
            response = supabase.auth.sign_up({"email": email, "password": password})
            print("Signed up successfully.")
            if response.session:
                return response.session.access_token
            else:
                print("Sign up successful but no session returned (check email confirmation settings).")
                # Try signing in again just in case auto-confirm is on
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                return response.session.access_token
        except Exception as e2:
            print(f"Authentication failed: {e2}")
            exit(1)

def main():
    # 1. Get Auth Token
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a Device
    device_id = 63
    device_payload = {
        "device_id": device_id,
        "name": "My Test Raspberry Pi"
    }
    
    print(f"\nCreating device '{device_id}'...")
    response = requests.post(f"{API_URL}/devices/create", json=device_payload, headers=headers)
    
    if response.status_code == 200:
        print("Device created successfully:", response.json())
    elif response.status_code == 400 and "already registered" in response.text:
         print("Device already exists.")
    else:
        print("Failed to create device:", response.status_code, response.text)
        exit(1)

    # 3. Ingest Data (Simulating RPI)
    # Note: Ingestion typically doesn't require User Auth header if following the plan, 
    # but the router implementation might vary. 
    # Looking at telemetry.py: @router.post("/ingest/{device_id}") has NO dependency on get_current_user.
    # So we don't send headers here to simulate the RPI.
    for i in range(4):
        telemetry_payload = {
            "potentiometer_value": 0.75,
            "image_data": "https://example.com/image.jpg",
            "timestamp": "2023-10-27T10:00:00Z"
        }
        
        print(f"\nIngesting data for '{device_id}'...")
        # The schema expects the body to be wrapped in "payload" key? 
        # Checking app/routers/telemetry.py: 
        # def ingest_data(device_id: str, payload: TelemetryPayload):
        # So it expects the fields directly in the body matching TelemetryPayload.
        
        response = requests.post(f"{API_URL}/ingest/{device_id}", json=telemetry_payload)
        
        if response.status_code == 200:
            print("Data ingested successfully:", response.json())
        else:
            print("Failed to ingest data:", response.status_code, response.text)

    # 4. Get Device Data (User Auth Required)
    print(f"\nRetrieving data for '{device_id}'...")
    response = requests.get(f"{API_URL}/devices/get/{device_id}/data", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Retrieved {len(data)} records.")
        if len(data) > 0:
            print("All records:", data)
    else:
        print("Failed to retrieve data:", response.status_code, response.text)

    # 5. Get All User Data (User Auth Required)
    print(f"\nRetrieving ALL data for user...")
    response = requests.get(f"{API_URL}/devices/get_all_data", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Retrieved {len(data)} total records across all devices.")
        if len(data) > 0:
            print("All records:", data)
    else:
        print("Failed to retrieve all data:", response.status_code, response.text)

if __name__ == "__main__":
    main()
