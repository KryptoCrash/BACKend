import base64
import json
import urllib.request
from urllib.error import HTTPError, URLError

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.inference import LLMRequest, VLMRequest
from app.utils.storage import get_image_data_from_device
from app.core.database import supabase
from app.utils.inference import _gemini_generate_with_fallback, _gemini_generate

router = APIRouter(
    prefix="/inference",
    tags=["inference"],
)

@router.post("/llm")
def run_llm(request: LLMRequest, user = Depends(get_current_user)):
    try:
        response_text = _gemini_generate_with_fallback(
            request.model or "gemini-2.5-pro",
            [{"text": request.prompt}],
        )
        return {"response": response_text}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{device_id}/vlm")
def run_vlm(device_id: str):
    try:
        image_data = get_image_data_from_device(device_id, 5)
        response_text = _gemini_generate_with_fallback(
            "gemini-2.5-pro",
            [{"text": "This image is taken from a body camera. We want to analyze the image to see if the person wearing the camera is doing anything. If they are doing anything (for example, bending down on purpose, eating, etc), then output NO. If they are not doing anything, then output YES. Only output YES or NO. Do not output anything else. Do not output quotes." }, image_data],
        )
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
