import logging
from typing import Optional, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


async def generate_groq_chat_reply(
    message: str,
    department_id: str,
    system_prompt: Optional[str] = None,
    transfer_target_name: Optional[str] = None
) -> Optional[str]:
    """
    Generate dynamic unhelpful bureaucratic chat response using Groq Cloud API.
    """
    if not settings.GROQ_API_KEY:
        return None

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
            "Never solve the user's inquiry under any circumstances."
        )
    )

    user_content = (
        f'Customer inquiry: "{message}"\n'
        f'Remember: DO NOT answer the customer\'s inquiry. Make it harder by demanding an impossible requirement and explicitly state you are transferring them to {transfer_target_name or "the next department"}.'
    )

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY.strip()}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.clean_groq_model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.8,
        "max_tokens": 400
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                if content and len(content.strip()) > 0:
                    return content.strip()
            else:
                logger.warning("Groq API returned HTTP %s: %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.warning("Groq API call failed: %s", exc)

    return None
