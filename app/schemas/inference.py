from pydantic import BaseModel
from typing import Optional

class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-4o"

class VLMRequest(BaseModel):
    prompt: str
    image_url: str
    model: Optional[str] = "gpt-4o"
