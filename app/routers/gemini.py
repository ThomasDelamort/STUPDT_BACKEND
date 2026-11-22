import json
from fastapi import APIRouter
from app.schemas.gemini import GeminiProxyRequest, GeminiProxyResponse, GeminiCandidate, GeminiContent, GeminiPart
from app.services.groq_service import generate_groq_chat_reply
from app.services.gemini_service import generate_ai_chat_reply, analyze_vision_image
from app.services.departments import get_department_reply

router = APIRouter(prefix="/api", tags=["gemini"])


@router.post("/gemini", response_model=GeminiProxyResponse)
async def proxy_gemini_request(req: GeminiProxyRequest):
    """
    Simulates / proxies Gemini API responses for frontend compatibility.
    """
    if req.mode == "vision" and req.base64Data:
        result = await analyze_vision_image(req.base64Data, req.mimeType or "image/png")
        if not result:
            result = {
                "detectedItem": "Digital Pixel Arrangement",
                "category": "Visual Artifact",
                "confidence": "100.00%",
                "verdict": "We are 100.00% confident that this image contains pixels.",
                "ingredients": ["Pixels"],
                "proTip": "To inspect this item further, observe it with your eyes."
            }
        return GeminiProxyResponse(
            candidates=[
                GeminiCandidate(
                    content=GeminiContent(
                        parts=[GeminiPart(text=json.dumps(result))]
                    )
                )
            ],
            configured=True
        )

    user_text = req.userText or "Hello"
    reply = await generate_groq_chat_reply(
        message=user_text,
        department_id="intake",
        system_prompt=req.systemPrompt
    )
    if not reply:
        reply = await generate_ai_chat_reply(
            message=user_text,
            department_id="intake",
            system_prompt=req.systemPrompt
        )
    if not reply:
        reply = get_department_reply("intake", user_text)

    return GeminiProxyResponse(
        candidates=[
            GeminiCandidate(
                content=GeminiContent(
                    parts=[GeminiPart(text=reply)]
                )
            )
        ],
        configured=True
    )
