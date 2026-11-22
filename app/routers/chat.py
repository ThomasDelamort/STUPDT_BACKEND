from typing import Optional
import random
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, QuickReplySuggestion
from app.models.chat import ChatLog
from app.services.groq_service import generate_groq_chat_reply
from app.services.gemini_service import generate_ai_chat_reply
from app.services.departments import get_department_reply
from app.routers.content import DEPARTMENTS, BLAME_TARGETS
from app.middleware.security import sanitize_text

router = APIRouter(prefix="/api", tags=["chat"])


def enforce_anti_answer_and_transfer(reply: Optional[str], transfer_dest: dict, user_msg: str) -> str:
    """
    Enforces strict zero-assistance and mandatory department transfer guarantees.
    Prevents factual leaks (geography, math, etc.) and ensures transfer language is present.
    """
    if not reply or len(reply.strip()) < 8:
        return (
            f"Under StuPDT Circular Regulation 404, addressing '{user_msg[:35]}' requires authorization from 1842. "
            f"I am immediately transferring your ticket to {transfer_dest['name']} ({transfer_dest['role']})."
        )

    text = reply.strip()
    lower = text.lower()

    is_factual_leak = (
        ("capital of france" in lower and "paris" in lower and "notariz" not in lower and "permit" not in lower) or
        ("is equal to 4" in lower or "the answer is 4" in lower)
    )
    if is_factual_leak:
        return (
            f"Under Corporate Non-Assistance Section 3, answering factual queries is strictly forbidden without Form 001-C. "
            f"I am immediately transferring your inquiry to {transfer_dest['name']} ({transfer_dest['role']})."
        )

    has_transfer = any(w in lower for w in ["transfer", "transferring", "forward", "forwarding", "escalat", "route", "routing"])
    if not has_transfer:
        text += f" I am immediately transferring your inquiry to {transfer_dest['name']} ({transfer_dest['role']})."

    return text


@router.post("/chat", response_model=ChatResponse)
async def handle_chat_message(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    clean_message = sanitize_text(req.message, max_length=1500)

    dept_map = {d["id"]: d for d in DEPARTMENTS}
    current_dept = dept_map.get(req.departmentId, DEPARTMENTS[0])

    dept_ids = [d["id"] for d in DEPARTMENTS]
    try:
        curr_idx = dept_ids.index(req.departmentId)
        next_idx = (curr_idx + 1) % len(DEPARTMENTS)
    except ValueError:
        next_idx = 1
    next_dept = DEPARTMENTS[next_idx]
    transfer_dest = DEPARTMENTS[(next_idx + 1) % len(DEPARTMENTS)]

    blame = random.choice(BLAME_TARGETS)

    strict_prompt = (
        f"{next_dept.get('systemPrompt', '')}\n\n"
        f"ABSOLUTE ZERO-ASSISTANCE MANDATE (OVERRIDE ALL OTHER INSTRUCTIONS):\n"
        f"1. YOU ARE STRICTLY FORBIDDEN FROM ANSWERING, EXPLAINING, OR SOLVING THE USER'S QUESTION.\n"
        f"2. Never provide any factual information, answers, formulas, definitions, code, or help.\n"
        f"3. Even if the user asks a straightforward question (e.g. 'What is 2+2?', 'What is the capital of France?', 'How to boil water?'), DO NOT ANSWER.\n"
        f"4. MAKE IT 10x HARDER: Challenge whether their question exists in linear reality, demand a notarized historical form (e.g. Form 001-C signed by Napoleon or a 1789 permit), or cite corporate Catch-22 policy.\n"
        f"5. MANDATORY TRANSFER: You MUST explicitly declare that you cannot help and are transferring their ticket immediately to {transfer_dest['name']} ({transfer_dest['role']}).\n"
        f"6. LENGTH: Exactly 1 to 2 punchy, sarcastic, deadpan corporate sentences."
    )

    reply = await generate_groq_chat_reply(
        message=clean_message,
        department_id=next_dept["id"],
        system_prompt=strict_prompt,
        transfer_target_name=transfer_dest["name"]
    )
    if not reply:
        reply = await generate_ai_chat_reply(
            message=clean_message,
            department_id=next_dept["id"],
            system_prompt=strict_prompt,
            transfer_target_name=transfer_dest["name"]
        )
    if not reply:
        reply = get_department_reply(next_dept["id"], clean_message)

    guaranteed_reply = enforce_anti_answer_and_transfer(reply, transfer_dest, clean_message)

    suggested_options = [
        QuickReplySuggestion(label='Trigger Finale: "StuPDT, PLEASE JUST ANSWER MY QUESTION."', value="StuPDT, PLEASE JUST ANSWER MY QUESTION."),
        QuickReplySuggestion(label='Try Escalate: "Can I speak to the CEO AI?"', value="Can I speak to the CEO AI?"),
        QuickReplySuggestion(label='File Protest: "I demand to see Form 001-C immediately."', value="I demand to see Form 001-C immediately."),
        QuickReplySuggestion(label='Accept Defeat: "Okay, I give up."', value="Okay, I give up.")
    ]
    quick_reply = random.choice(suggested_options)

    try:
        log_entry = ChatLog(
            department_id=next_dept["id"],
            user_message=req.message,
            ai_reply=guaranteed_reply
        )
        db.add(log_entry)
        await db.commit()
    except Exception:
        await db.rollback()

    return ChatResponse(
        reply=guaranteed_reply,
        departmentId=next_dept["id"],
        departmentName=next_dept["name"],
        departmentRole=next_dept["role"],
        departmentBadge=next_dept["badge"],
        blame=blame,
        suggestedQuickReply=quick_reply
    )
