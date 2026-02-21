from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import devices, telemetry, inference
from app.core.config import settings

app = FastAPI(title="RPI Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(devices.router)
app.include_router(telemetry.router)
app.include_router(inference.router)

@app.get("/")
def root():
    return {"message": "Welcome to the RPI Backend API"}
