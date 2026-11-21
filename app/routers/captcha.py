import time
import random
import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/captcha", tags=["captcha"])

CAPTCHA_CATEGORIES = [
    {
        "targetType": "traffic-light",
        "targetLabel": "a TRAFFIC LIGHT",
        "targetNamePlural": "Traffic Lights",
        "items": [
            {"iconType": "traffic-light", "label": "Traffic Light"},
            {"iconType": "traffic-light", "label": "Red Stop Signal"},
            {"iconType": "traffic-light", "label": "Pedestrian Light"},
        ],
    },
    {
        "targetType": "flame",
        "targetLabel": "a SERVER FIRE / FLAME",
        "targetNamePlural": "Fire / Flame Squares",
        "items": [
            {"iconType": "flame", "label": "Server Room"},
            {"iconType": "flame", "label": "GPU Overheat"},
            {"iconType": "flame", "label": "Flaming Router"},
        ],
    },
    {
        "targetType": "bot",
        "targetLabel": "an AI / ROBOT",
        "targetNamePlural": "AI Bots",
        "items": [
            {"iconType": "bot", "label": "Our CEO AI"},
            {"iconType": "bot", "label": "Intake Bot"},
            {"iconType": "bot", "label": "Bureaucracy Bot"},
        ],
    },
    {
        "targetType": "mountain",
        "targetLabel": "a ROCK / MOUNTAIN",
        "targetNamePlural": "Rock / Mountain Squares",
        "items": [
            {"iconType": "mountain", "label": "Just a Rock"},
            {"iconType": "mountain", "label": "Granite Peak"},
            {"iconType": "mountain", "label": "Bureaucratic Stone"},
        ],
    },
    {
        "targetType": "utensils",
        "targetLabel": "FOOD / SPAGHETTI",
        "targetNamePlural": "Food Squares",
        "items": [
            {"iconType": "utensils", "label": "Pure Spaghetti"},
            {"iconType": "utensils", "label": "Cold Ramen"},
            {"iconType": "utensils", "label": "Code Spaghetti"},
        ],
    },
    {
        "targetType": "briefcase",
        "targetLabel": "a BRIEFCASE / TICKET",
        "targetNamePlural": "Briefcase / Ticket Squares",
        "items": [
            {"iconType": "briefcase", "label": "Unread Ticket"},
            {"iconType": "briefcase", "label": "Executive Suitcase"},
            {"iconType": "briefcase", "label": "Lost Form 001"},
        ],
    },
]

CAPTCHA_DISTRACTORS = [
    {"iconType": "mountain", "label": "Just a Rock"},
    {"iconType": "utensils", "label": "Pure Spaghetti"},
    {"iconType": "briefcase", "label": "Unread Ticket"},
    {"iconType": "bot", "label": "Our CEO AI"},
    {"iconType": "timer", "label": "Loading at 99%"},
    {"iconType": "flame", "label": "Server Room"},
    {"iconType": "traffic-light", "label": "Traffic Light"},
    {"iconType": "mountain", "label": "Distant Hill"},
    {"iconType": "utensils", "label": "Office Lunch"},
    {"iconType": "briefcase", "label": "Paperwork"},
    {"iconType": "bot", "label": "Customer Bot"},
    {"iconType": "timer", "label": "Frozen Spinner"},
]

LEGAL_MATH_PROBLEMS = [
    {
        "id": "dept-math",
        "question": "StuPDT transfers you to 4 departments. Each department transfers you to 3 more departments. Together they solve 0 problems. What is (4 × 3) + 0?",
        "answer": "12",
        "hint": "CLASSIFIED LEAK (DO NOT SHARE): 4 × 3 is 12, and adding 0 solved problems keeps it at 12. Please don't tell the CEO AI I helped you.",
    },
    {
        "id": "form-math",
        "question": "You fill out Form 001, Form 001-A, and Form 001-B, taking 5 minutes each. How many total minutes did you just waste?",
        "answer": "15",
        "hint": "SECRET MEMO: 3 useless forms × 5 minutes each = 15 minutes of your life you will never get back. Type 15.",
    },
    {
        "id": "loading-math",
        "question": "Our loading bar is permanently stuck at 99%. How many percent are left that will never load? Multiply that remaining number by 7.",
        "answer": "7",
        "hint": "WHISTLEBLOWER FORMULA: 100 - 99 = 1%. Multiply 1 × 7 = 7. This Math Specialist is risking termination for telling you.",
    },
    {
        "id": "synergy-math",
        "question": "Our synergy committee spent 6 hours deciding to do nothing, then scheduled a 4-hour follow-up meeting. What is 6 + 4?",
        "answer": "10",
        "hint": "CONFIDENTIAL LEAK: 6 wasted hours + 4 more wasted hours = 10 total wasted hours. Type 10.",
    },
    {
        "id": "ticket-math",
        "question": "There are 50 tickets in the queue. Department #001 answers 0, Department #002 deletes 20, and Department #003 loses 30. How many tickets were actually solved?",
        "answer": "0",
        "hint": "INSIDER TRUTH: Exactly 0 problems were solved. It's always 0 at StuPDT. Type 0.",
    },
    {
        "id": "chaos-math",
        "question": "The Chaos Meter started at 80% and increased by 8% after Mercury entered retrograde. What is 80 + 8?",
        "answer": "88",
        "hint": "ASTROLOGICAL ARITHMETIC: 80 + 8 = 88. Type 88 before Mercury goes direct.",
    },
]

# Server-side challenge store (challenge_id -> state)
SERVER_CHALLENGES: Dict[str, Dict[str, Any]] = {}


def cleanup_expired_challenges():
    """Removes challenges older than 15 minutes."""
    now = time.time()
    expired = [cid for cid, ch in SERVER_CHALLENGES.items() if now - ch["createdAt"] > 900]
    for cid in expired:
        SERVER_CHALLENGES.pop(cid, None)


class VerifyTilesRequest(BaseModel):
    challengeId: str = Field(..., max_length=64, description="Server challenge session ID")
    selectedIds: List[int] = Field(default=[], max_length=16, description="Selected tile indices")


class VerifyMathRequest(BaseModel):
    challengeId: str = Field(..., max_length=64, description="Server challenge session ID")
    answer: str = Field(..., max_length=50, description="User submitted arithmetic answer")


@router.get("/challenge")
@router.get("")
async def generate_captcha_challenge(exclude: str | None = None):
    cleanup_expired_challenges()

    # Select random category
    eligible = [c for c in CAPTCHA_CATEGORIES if c["targetType"] != exclude]
    category = random.choice(eligible or CAPTCHA_CATEGORIES)

    # 3 target items
    target_items = [
        {"iconType": item["iconType"], "label": item["label"], "is_target": True}
        for item in category["items"][:3]
    ]

    # 6 distractors
    distractors_pool = [d for d in CAPTCHA_DISTRACTORS if d["iconType"] != category["targetType"]]
    random.shuffle(distractors_pool)
    distractor_items = [
        {"iconType": d["iconType"], "label": d["label"], "is_target": False}
        for d in distractors_pool[:6]
    ]

    # Combine and shuffle
    combined = target_items + distractor_items
    random.shuffle(combined)

    client_tiles = []
    correct_ids = []
    for idx, item in enumerate(combined):
        client_tiles.append({
            "id": idx,
            "iconType": item["iconType"],
            "label": item["label"]
            # Notice: is_target is NEVER sent to the client!
        })
        if item["is_target"]:
            correct_ids.append(idx)

    # Select random math problem
    math_prob = random.choice(LEGAL_MATH_PROBLEMS)

    # Store server-side verification record
    challenge_id = str(uuid.uuid4())
    SERVER_CHALLENGES[challenge_id] = {
        "targetType": category["targetType"],
        "targetLabel": category["targetLabel"],
        "targetNamePlural": category["targetNamePlural"],
        "correctIds": set(correct_ids),
        "mathAnswer": math_prob["answer"].strip(),
        "mathHint": math_prob["hint"],
        "createdAt": time.time()
    }

    return {
        "challengeId": challenge_id,
        "targetLabel": category["targetLabel"],
        "targetNamePlural": category["targetNamePlural"],
        "count": len(correct_ids),
        "tiles": client_tiles,
        "mathProblem": {
            "id": math_prob["id"],
            "question": math_prob["question"]
            # Notice: answer and hint are NEVER sent to the client!
        }
    }


@router.post("/verify-tiles")
async def verify_captcha_tiles(req: VerifyTilesRequest):
    challenge = SERVER_CHALLENGES.get(req.challengeId)
    if not challenge:
        return {
            "valid": False,
            "error": "Security ticket expired. Please close and re-open to generate a new puzzle."
        }

    user_set = set(req.selectedIds)
    if user_set == challenge["correctIds"]:
        return {
            "valid": True,
            "message": "Human verification successful."
        }

    return {
        "valid": False,
        "error": f"Suspiciously robotic click detected. Try clicking ONLY the {len(challenge['correctIds'])} actual {challenge['targetNamePlural']}!"
    }


@router.post("/verify-math")
async def verify_captcha_math(req: VerifyMathRequest):
    challenge = SERVER_CHALLENGES.get(req.challengeId)
    if not challenge:
        return {
            "approved": False,
            "error": "Permit session expired. Please restart the verification."
        }

    if req.answer.strip() == challenge["mathAnswer"]:
        # Consume the challenge so it cannot be reused
        SERVER_CHALLENGES.pop(req.challengeId, None)
        return {
            "approved": True,
            "message": "FORM LT-001 APPROVED! Deploying Retina-Scorching Alpine Light Mode!"
        }

    return {
        "approved": False,
        "error": "Incorrect arithmetic! Our server hamsters have rejected your brightness permit. Try again (or ask the Math Specialist for a hint)!"
    }


@router.get("/math-hint")
async def get_math_hint(challengeId: str):
    challenge = SERVER_CHALLENGES.get(challengeId)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge session not found.")
    return {
        "hint": challenge["mathHint"]
    }
