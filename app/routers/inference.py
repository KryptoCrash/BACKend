from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.inference import LLMRequest, VLMRequest
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

router = APIRouter(
    prefix="/inference",
    tags=["inference"],
)

@router.post("/llm")
def run_llm(request: LLMRequest, user = Depends(get_current_user)):
    try:
        completion = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "user", "content": request.prompt}
            ]
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vlm")
def run_vlm(request: VLMRequest, user = Depends(get_current_user)):
    try:
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": request.prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": request.image_url,
                            },
                        },
                    ],
                }
            ],
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
