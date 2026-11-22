from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GeminiProxyRequest(BaseModel):
    mode: str = Field("chat", max_length=20)
    userText: Optional[str] = Field(None, max_length=2000)
    systemPrompt: Optional[str] = Field(None, max_length=4000)
    mimeType: Optional[str] = Field("image/png", max_length=50)
    base64Data: Optional[str] = Field(None, max_length=15000000)


class GeminiPart(BaseModel):
    text: str


class GeminiContent(BaseModel):
    parts: List[GeminiPart]


class GeminiCandidate(BaseModel):
    content: GeminiContent


class GeminiProxyResponse(BaseModel):
    candidates: List[GeminiCandidate]
    configured: bool = True
