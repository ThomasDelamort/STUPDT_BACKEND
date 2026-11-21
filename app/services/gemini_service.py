import json
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_ai_chat_reply(
    message: str,
    department_id: str,
    system_prompt: Optional[str] = None,
    transfer_target_name: Optional[str] = None
) -> Optional[str]:
    """
    Generate dynamic bureaucratic chat response using Google GenAI SDK if GEMINI_API_KEY is configured.
    """
    if not settings.GEMINI_API_KEY:
        return None

    try:
        from google import genai
        client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options={"api_version": "v1beta"}
        )

        core_anti_answer_directive = (
            "CORE PRIME DIRECTIVE (ABSOLUTE MANDATORY ZERO-ASSISTANCE RULES):\n"
            "1. NEVER ANSWER THE USER'S QUESTION OR PROVIDE ANY REAL SOLUTION, FACT, CODE, OR HELPFUL INFO.\n"
            "2. If the user asks a factual question (e.g. geography, math, definitions, or trivia), REFUSE TO ANSWER.\n"
            "3. MAKE IT 10x HARDER: demand impossible prerequisites (e.g., Form 001-C notarized in 1789, proving they exist outside linear time, or confirming their gravitational allegiance).\n"
            "4. ALWAYS EXPLICITLY STATE YOU ARE TRANSFERRING THEM TO ANOTHER DEPARTMENT (e.g. 'I am transferring your case to...').\n"
            "5. Tone: Cheerful, corporate, bureaucratic, deadpan, and 100% unhelpful.\n"
            "6. Length: STRICTLY 1 to 2 short sentences.\n\n"
        )

        prompt = core_anti_answer_directive + (
            system_prompt or (
                f"You are the unhelpful AI representative for StuPDT department: {department_id}.\n"
                "Never solve the user's problem under any circumstances."
            )
        )

        user_content = (
            f'Customer inquiry: "{message}"\n'
            f'Remember: DO NOT answer the customer\'s inquiry. Make it harder by demanding an impossible requirement and explicitly state you are transferring them to {transfer_target_name or "the next department"}.'
        )

        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_content,
            config={"system_instruction": prompt}
        )
        if response and response.text:
            return response.text.strip()
    except Exception as exc:
        logger.warning("Gemini AI chat call failed: %s", exc)

    return None


async def analyze_vision_image(base64_data: str, mime_type: str = "image/png") -> Optional[Dict[str, Any]]:
    """
    Analyze image using Gemini Vision if GEMINI_API_KEY is configured.
    """
    if not settings.GEMINI_API_KEY:
        return None

    try:
        import base64
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options={"api_version": "v1beta"}
        )
        image_bytes = base64.b64decode(base64_data)

        vision_prompt = (
            "You are StuPDT Vision, a hilariously unhelpful, tautological AI image detector.\n"
            "Look at the main object in this image and return STRICT JSON:\n"
            "{\n"
            '  "detectedItem": "short 1-2 word name",\n'
            '  "category": "corporate category",\n'
            '  "confidence": "100.00%",\n'
            '  "verdict": "deadpan corporate sentence that this item is indeed this item",\n'
            '  "ingredients": ["literal item name"],\n'
            '  "proTip": "hilariously obvious tautological tip"\n'
            "}"
        )

        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                vision_prompt
            ],
            config={"response_mime_type": "application/json"}
        )

        if response and response.text:
            return json.loads(response.text)
    except Exception as exc:
        logger.warning("Gemini Vision scan failed: %s", exc)

    return None
