import base64
import json
import urllib.request
from urllib.error import HTTPError, URLError

from fastapi import HTTPException

from app.core.config import settings


def _gemini_generate(model: str, parts: list[dict]) -> str:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")

    normalized_model = (model or "gemini-2.5-pro").replace("models/", "")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{normalized_model}:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore") or str(e)
        raise HTTPException(status_code=e.code, detail=f"Gemini HTTP error: {detail}")
    except URLError as e:
        raise HTTPException(status_code=500, detail=f"Gemini connection error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini request failed: {e}")

    candidates = body.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=500, detail="Gemini returned no candidates")

    content_parts = candidates[0].get("content", {}).get("parts", [])
    text_chunks = [p.get("text", "") for p in content_parts if p.get("text")]
    response_text = "\n".join(text_chunks).strip()
    if not response_text:
        raise HTTPException(status_code=500, detail="Gemini returned empty text")
    return response_text


def _gemini_generate_with_fallback(requested_model: str, parts: list[dict]) -> str:
    candidates = []
    if requested_model:
        candidates.append(requested_model)
    candidates.extend([
        "gemini-2.5-pro",
        "gemini-pro-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ])
    # Preserve order while removing duplicates
    seen = set()
    models_to_try = []
    for m in candidates:
        key = m.replace("models/", "")
        if key in seen:
            continue
        seen.add(key)
        models_to_try.append(key)

    last_error: HTTPException | None = None
    for model in models_to_try:
        try:
            return _gemini_generate(model, parts)
        except HTTPException as e:
            last_error = e
            # Retry on model-not-found; surface other failures immediately.
            if e.status_code != 404:
                raise e

    raise last_error or HTTPException(status_code=500, detail="Gemini generation failed")


def _fetch_image_as_inline_data(image_url: str) -> dict:
    try:
        with urllib.request.urlopen(image_url, timeout=30) as img_resp:
            img_bytes = img_resp.read()
            mime_type = img_resp.headers.get_content_type() or "image/jpeg"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image_url: {e}")

    if not mime_type.startswith("image/"):
        mime_type = "image/jpeg"
    if not img_bytes:
        raise HTTPException(status_code=400, detail="Image URL returned empty content")

    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": base64.b64encode(img_bytes).decode("utf-8"),
        }
    }