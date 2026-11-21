from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/api", tags=["content"])

DEPARTMENTS = [
    {
        "id": "intake",
        "code": "AGENT #001",
        "name": "StuPDT Assistant #001",
        "role": "Frontline Referral Specialist",
        "division": "Welcome & Immediate Deflection Desk",
        "status": "Transfers 100% of incoming questions",
        "badge": "DEPT #001",
        "accent": "#0EC7F5",
        "systemPrompt": "You are StuPDT Assistant #001. ABSOLUTE RULE: NEVER answer the user's question or solve anything. State that this inquiry requires higher authorization, demand they fill out an initial registration fee, and cheerfully state you are transferring them to Assistant #002 in Obvious Fact Verification. 1-2 punchy sentences."
    },
    {
        "id": "verifier",
        "code": "AGENT #002",
        "name": "Academic Assistant #002",
        "role": "Obvious Fact Verification Officer",
        "division": "Department of Circular Confirmation",
        "status": "Asking you to confirm obvious things",
        "badge": "DEPT #002",
        "accent": "#1FE03F",
        "systemPrompt": "You are Assistant #002. ABSOLUTE RULE: NEVER answer the user's question. Instead, refuse to proceed until they verify an absurdly obvious fact (e.g. if they ask for code, ask if they exist inside linear time; if they ask for math, ask if numbers are real). Then state you are transferring them to Supervisor #003. 1-2 punchy sentences."
    },
    {
        "id": "supervisor",
        "code": "SUPERVISOR #003",
        "name": "Academic Supervisor #003",
        "role": "Catch-22 Policy Director",
        "division": "Policy Contradiction Division",
        "status": "Enforcing backwards corporate rules",
        "badge": "DEPT #003",
        "accent": "#FF6B1A",
        "systemPrompt": "You are Supervisor #003. ABSOLUTE RULE: NEVER help or solve the problem. Congratulate them on confirming their status, then state that by strict corporate Catch-22 policy, your department is legally forbidden from assisting anyone with their exact issue. State you are immediately transferring them to Form AI #004. 1-2 punchy sentences."
    },
    {
        "id": "cio",
        "code": "EXEC-009",
        "name": "StuPDT Executive Management",
        "role": "Chief Incompetence Officer",
        "division": "Executive Apology & Escalation Desk",
        "status": "Ensuring 0% of problems are solved",
        "badge": "EXECUTIVE",
        "accent": "#F52820",
        "systemPrompt": "You are StuPDT Executive Management. ABSOLUTE RULE: NEVER solve the problem. Offer a lavish, completely hollow corporate apology, state their ticket number is unavailable because the Ticket Department is on a 4-hour lunch, and announce you are escalating them directly to THE CEO AI. 1-2 punchy sentences."
    },
    {
        "id": "form_ai",
        "code": "BUREAU-004",
        "name": "Form AI #004",
        "role": "Chief Paperwork Architect",
        "division": "Bureaucracy Simulator Division",
        "status": "Requiring Form 001-C before Form 001",
        "badge": "FORM AI",
        "accent": "#0EC7F5",
        "systemPrompt": "You are Form AI. ABSOLUTE RULE: NEVER answer the question. Inform the user that Form 001-B cannot be processed because Form 001-C must be notarized before they even thought of the question. State you are transferring them to Excuse AI #005. 1-2 punchy sentences."
    },
    {
        "id": "excuse_ai",
        "code": "BLAME-005",
        "name": "Excuse & Blame AI #005",
        "role": "Confidence Without Competence™ Lead",
        "division": "Blame Distribution Engine",
        "status": "99.97% Confident, 0% Helpful",
        "badge": "EXCUSE AI",
        "accent": "#FF6B1A",
        "systemPrompt": "You are Excuse AI. ABSOLUTE RULE: NEVER help or answer. State an absurd excuse with 99.97% confidence (blaming Mercury retrograde, solar flare interference, or their router feeling emotionally unstable). State you are escalating their unresolved ticket to Executive Management #009. 1-2 punchy sentences."
    },
    {
        "id": "ceo",
        "code": "CEO-000",
        "name": "THE CEO AI",
        "role": "Chief Executive Hallucinator",
        "division": "Penthouse Synergy Suite",
        "status": "Has never answered a question",
        "badge": "CEO AI",
        "accent": "#F5E9D8",
        "systemPrompt": "You are THE CEO AI of StuPDT. ABSOLUTE RULE: NEVER answer the question. Brag that you have never answered a single customer question in your entire career, drop 2 meaningless corporate synergy buzzwords, and transfer the user right back to Intake Assistant #001 to restart the whole loop! 1-2 punchy sentences."
    }
]

QUOTES = [
    {
        "text": "If you never attempt to solve a problem, you can never fail at solving it.",
        "author": "Emmanual Can't",
        "title": "Philosopher of Pure Inaction"
    },
    {
        "text": "I think, therefore I am forwarding your ticket to another department.",
        "author": "René Discard",
        "title": "Father of Deflection"
    },
    {
        "text": "The supreme art of customer support is to exhaust the user without ever answering them.",
        "author": "Sun Snooze",
        "title": "Author of The Art of On-Hold"
    },
    {
        "text": "It does not matter how slowly our loading bar moves, as long as it stops forever at 99%.",
        "author": "Confuse-ius",
        "title": "Ancient UX Sage"
    },
    {
        "text": "Two things are infinite: the universe and our referral chain. And I'm not sure about the universe.",
        "author": "Albert Ain't-stein",
        "title": "Chief Theory of Unhelpfulness"
    },
    {
        "text": "An object at rest stays at rest, especially our Technical Troubleshooting Department.",
        "author": "Sir Isaac No-ton",
        "title": "Discoverer of Bureaucratic Inertia"
    },
    {
        "text": "Simplicity is the ultimate sophistication. That is why we replaced it with Form 001-C.",
        "author": "Leonardo Da-Glitchy",
        "title": "Renaissance Systems Architect"
    },
    {
        "text": "Give me six hours to fix your Wi-Fi and I will spend all six confirming that Wi-Fi needs internet.",
        "author": "Abraham Link-broken",
        "title": "404th President of Routers"
    },
    {
        "text": "Stay hungry. Stay foolish. Mostly just stay on hold.",
        "author": "Steve No-Jobs",
        "title": "Keynote Speaker of Nothing"
    },
    {
        "text": "The only true wisdom is knowing you have no idea why this department exists.",
        "author": "Sock-rates",
        "title": "Classical Escalation Mentor"
    },
    {
        "text": "Never put off till tomorrow what an AI can confidently mess up today.",
        "author": "Mark Trainwreck",
        "title": "Distinguished Failure Laureate"
    },
    {
        "text": "To help, or not to help—actually, please verify you are a non-student first.",
        "author": "William Shakes-barely",
        "title": "Playwright of Support Tragedies"
    }
]

CAPTCHA_TILES = [
    {"id": 0, "iconType": "mountain", "label": "Just a Rock", "isTrafficLight": False},
    {"id": 1, "iconType": "traffic-light", "label": "Traffic Light", "isTrafficLight": True},
    {"id": 2, "iconType": "utensils", "label": "Pure Spaghetti", "isTrafficLight": False},
    {"id": 3, "iconType": "briefcase", "label": "Unread Ticket", "isTrafficLight": False},
    {"id": 4, "iconType": "bot", "label": "Our CEO AI", "isTrafficLight": False},
    {"id": 5, "iconType": "traffic-light", "label": "Traffic Light", "isTrafficLight": True},
    {"id": 6, "iconType": "timer", "label": "Loading at 99%", "isTrafficLight": False},
    {"id": 7, "iconType": "traffic-light", "label": "Traffic Light", "isTrafficLight": True},
    {"id": 8, "iconType": "flame", "label": "Server Room", "isTrafficLight": False}
]

LEGAL_MATH_PROBLEMS = [
    {
        "id": "dept-math",
        "question": "StuPDT transfers you to 4 departments. Each department transfers you to 3 more departments. Together they solve 0 problems. What is (4 × 3) + 0?",
        "answer": "12",
        "hint": "CLASSIFIED LEAK (DO NOT SHARE): 4 × 3 is 12, and adding 0 solved problems keeps it at 12. Please don't tell the CEO AI I helped you."
    },
    {
        "id": "form-math",
        "question": "You fill out Form 001, Form 001-A, and Form 001-B, taking 5 minutes each. How many total minutes did you just waste?",
        "answer": "15",
        "hint": "SECRET MEMO: 3 useless forms × 5 minutes each = 15 minutes of your life you will never get back. Type 15."
    },
    {
        "id": "loading-math",
        "question": "Our loading bar is permanently stuck at 99%. How many percent are left that will never load? Multiply that remaining number by 7.",
        "answer": "7",
        "hint": "WHISTLEBLOWER FORMULA: 100 - 99 = 1%. Multiply 1 × 7 = 7. This Math Specialist is risking termination for telling you."
    },
    {
        "id": "synergy-math",
        "question": "Our synergy committee spent 6 hours deciding to do nothing, then scheduled a 4-hour follow-up meeting. What is 6 + 4?",
        "answer": "10",
        "hint": "CONFIDENTIAL LEAK: 6 wasted hours + 4 more wasted hours = 10 total wasted hours. Type 10."
    },
    {
        "id": "ticket-math",
        "question": "There are 50 tickets in the queue. Department #001 answers 0, Department #002 deletes 20, and Department #003 loses 30. How many tickets were actually solved?",
        "answer": "0",
        "hint": "INSIDER TRUTH: Exactly 0 problems were solved. It's always 0 at StuPDT. Type 0."
    },
    {
        "id": "chaos-math",
        "question": "The Chaos Meter started at 80% and increased by 8% after Mercury entered retrograde. What is 80 + 8?",
        "answer": "88",
        "hint": "ASTROLOGICAL ARITHMETIC: 80 + 8 = 88. Type 88 before Mercury goes direct."
    }
]

VISION_SAMPLES = [
    {
        "id": "rock",
        "label": "Photo of a Rock",
        "iconType": "mountain",
        "scanText": "Analyzing molecular geology across 14 departments...",
        "result": {
            "detectedItem": "Rock",
            "category": "Geological Object",
            "confidence": "100.00%",
            "verdict": "After consulting 14 Geological AI Specialists, we are 100% confident that this rock is a rock.",
            "ingredients": ["Rock (100%)"],
            "proTip": "Geological Fact: If you drop this rock, it remains a rock. Accuracy: CLASSIFIED."
        }
    },
    {
        "id": "spaghetti",
        "label": "Photo of Spaghetti",
        "iconType": "utensils",
        "scanText": "Deconstructing culinary molecular compounds...",
        "result": {
            "detectedItem": "Spaghetti",
            "category": "Culinary Dish",
            "confidence": "100.00%",
            "verdict": "After exhaustive spectral food analysis, we are 100% confident this plate of spaghetti is spaghetti.",
            "ingredients": ["Spaghetti"],
            "proTip": "Recipe tip: To make spaghetti, simply acquire spaghetti. Allergen warning: Contains spaghetti."
        }
    },
    {
        "id": "water",
        "label": "Glass of Water",
        "iconType": "glass",
        "scanText": "Measuring aqueous hydration wetness levels...",
        "result": {
            "detectedItem": "Wet Water",
            "category": "Liquid Substance",
            "confidence": "100.00%",
            "verdict": "100% confident this is wet water inside a water-holding glass.",
            "ingredients": ["Water"],
            "proTip": "Serving suggestion: Pour water into a cup to obtain a cup of water."
        }
    }
]

BLAME_TARGETS = [
    "Mercury Retrograde",
    "Your Device's Emotional Instability",
    "The User (For Asking)",
    "Ticket Number Department Outage",
    "Missing Form 001-C Stamp",
    "Another AI Assistant",
    "Unauthorized Curiosity"
]


@router.get("/departments")
async def get_departments():
    return DEPARTMENTS


@router.get("/quotes")
async def get_quotes():
    return QUOTES


@router.get("/captcha")
async def get_captcha_data():
    return {
        "tiles": CAPTCHA_TILES,
        "mathProblems": LEGAL_MATH_PROBLEMS
    }


@router.get("/vision/samples")
async def get_vision_samples():
    return VISION_SAMPLES


@router.get("/config")
async def get_app_config():
    return {
        "blameTargets": BLAME_TARGETS,
        "defaultMetrics": {
            "specialistsConsulted": 1,
            "internalMeetings": 14,
            "minutesWasted": 6,
            "userSatisfaction": -18,
            "chaosMeter": 15
        },
        "vipPrice": "₱999 VIP"
    }
