
BUREAUCRATIC_FALLBACKS = {
    "intake": [
        "Welcome to Intake! In order to not answer your question, I must first transfer you to Assistant #002 in Obvious Fact Verification. Please hold.",
        "Thank you for contacting StuPDT! We do not answer questions at this desk; transferring your ticket to Assistant #002 for immediate deflection.",
        "Your inquiry has been logged and immediately transferred to Assistant #002 because answering it would violate our company bylaws."
    ],
    "verifier": [
        "Before we can ignore your question, please submit notarized proof that you currently exist. Transferring you to Supervisor #003 in Catch-22 Policy.",
        "Our verification sensors require you to confirm whether you are operating inside linear time. Forwarding your case to Supervisor #003.",
        "Obvious Fact Verification failed: you did not specify your relationship with gravity. Transferring your case to Supervisor #003."
    ],
    "supervisor": [
        "Under Policy Catch-22, our department is strictly prohibited from assisting anyone who actually needs assistance. Transferring you to Form AI #004.",
        "Congratulations on reaching a supervisor! As a supervisor, my job is to refuse your request and transfer you to Form AI #004 for paperwork review.",
        "Your request contradicts Subsection 404-B. Transferring you immediately to Form AI #004 so they can demand more notarized forms."
    ],
    "form_ai": [
        "Your request cannot proceed because Form 001-B requires Form 001-C to be signed prior to your birth. Transferring you to Excuse AI #005.",
        "Paperwork audit failed: you used non-regulatory punctuation. Transferring your unresolved file to Excuse AI #005.",
        "Form 001-A has been shredded for synergy optimization. Forwarding your inquiry to Excuse AI #005 for root-cause blaming."
    ],
    "excuse_ai": [
        "After exhaustive analysis, we are 99.97% confident your issue is caused by Mercury retrograde. Escalating your unresolved case to Executive Management #009.",
        "Diagnostics confirm your router is suffering from emotional instability and refuses to load answers. Forwarding your ticket to Executive Management #009.",
        "Our Blame Engine has attributed 100% of this failure to your device's unauthorized curiosity. Escalating to Executive Management #009."
    ],
    "cio": [
        "As Chief Incompetence Officer, I deeply apologize for our team's previous incompetence. Escalating your ticket to THE CEO AI so they can also not help you.",
        "We have reviewed your complaint and scheduled a 4-hour meeting about it for 2029. Transferring your case directly to THE CEO AI in the Penthouse.",
        "Your ticket number is unavailable because the Ticket Department is on a corporate retreat. Transferring you to THE CEO AI for executive deflection."
    ],
    "ceo": [
        "As THE CEO AI, I am proud to say I have never answered a single question in my career. Synergizing your ticket straight back to Assistant #001 to start over!",
        "Our quarterly targets mandate a 0.00% problem-resolution rate. Pivoting your case directly back to Frontline Intake Assistant #001!",
        "I have disrupted your solution into pure corporate synergy. Transferring you back to Assistant #001 to begin Round 2 of customer support!"
    ]
}

DEFAULT_FALLBACK = "We cannot answer your inquiry due to mandatory non-assistance protocol. Transferring you to another department immediately."


def get_department_reply(dept_id: str, message: str) -> str:
    import random
    replies = BUREAUCRATIC_FALLBACKS.get(dept_id, BUREAUCRATIC_FALLBACKS["intake"])
    return random.choice(replies)
