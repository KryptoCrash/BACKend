from fastapi import FastAPI
from app.routers import devices, telemetry, inference
from app.core.config import settings

app = FastAPI(title="RPI Backend", version="1.0.0")

app.include_router(devices.router)
app.include_router(telemetry.router)
app.include_router(inference.router)

@app.get("/")
def root():
    return {"message": "Welcome to the RPI Backend API"}
