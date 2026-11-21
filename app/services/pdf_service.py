import datetime
import io
import uuid
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def generate_official_apology_pdf(
    recipient_name: Optional[str] = None,
    case_reason: Optional[str] = None
) -> bytes:
    """
    Generates an official multi-page satirical Apology Certificate PDF
    complete with stamps, disclaimers, signatures, and legal blame clauses.
    """
    name = (recipient_name or "Valued Unresolved Citizen").strip()
    reason = (case_reason or "General Grievance Against Unhelpful System").strip()
    case_id = f"STUPDT-AP-{datetime.datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    issue_date = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S UTC")

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # =========================================================================
    # PAGE 1: OFFICIAL CERTIFICATE OF CORPORATE REGRET
    # =========================================================================
    # Double Border
    c.setStrokeColor(colors.HexColor("#071638"))
    c.setLineWidth(3)
    c.rect(36, 36, width - 72, height - 72)
    c.setLineWidth(1)
    c.rect(42, 42, width - 84, height - 84)

    # Watermark
    c.saveState()
    c.setFont("Helvetica-Bold", 38)
    c.setFillColor(colors.HexColor("#F2F5F8"))
    c.translate(width / 2, height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "CERTIFIED ZERO LIABILITY")
    c.restoreState()

    # Header
    c.setFillColor(colors.HexColor("#071638"))
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(width / 2, height - 75, "STUPDT BUREAUCRACY & DEFLECTION SOLUTIONS™")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(width / 2, height - 89, "Department of Inaction, Circular Reasoning & Customer Exhaustion")

    # Certificate Title
    c.setFillColor(colors.HexColor("#F52820"))
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(width / 2, height - 128, "OFFICIAL CERTIFICATE OF EXECUTIVE REGRET")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawCentredString(width / 2, height - 143, f"FORM AP-999 // CASE ID: {case_id}")

    # Divider
    c.setStrokeColor(colors.HexColor("#0EC7F5"))
    c.setLineWidth(1.5)
    c.line(60, height - 158, width - 60, height - 158)

    # Presentation Line
    c.setFillColor(colors.HexColor("#071638"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(70, height - 188, "THIS NON-BINDING CONDOLENCE IS SOLEMNLY GRANTED TO:")
    c.setFont("Helvetica-Bold", 17)
    c.setFillColor(colors.HexColor("#0EC7F5"))
    c.drawString(70, height - 212, name[:45].upper())

    # Case Metadata Box
    c.setStrokeColor(colors.HexColor("#E2E8F0"))
    c.setFillColor(colors.HexColor("#F8FAFC"))
    c.rect(70, height - 275, width - 140, 50, fill=True, stroke=True)
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(80, height - 240, "OFFICIAL INCIDENT:")
    c.setFont("Helvetica", 8)
    c.drawString(185, height - 240, reason[:65])
    c.setFont("Helvetica-Bold", 8)
    c.drawString(80, height - 256, "DATE OF ISSUE:")
    c.setFont("Helvetica", 8)
    c.drawString(185, height - 256, issue_date)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(80, height - 270, "AUDIT RESULT:")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#F52820"))
    c.drawString(185, height - 270, "0.00% RESOLVED • 100.00% SYMBOLIC SYNERGY")

    # Certificate Body
    c.setFillColor(colors.HexColor("#1E293B"))
    c.setFont("Helvetica", 9.5)
    body_lines = [
        "WHEREAS the citizen named above attempted in good faith to resolve an inquiry with our platform,",
        "AND WHEREAS our frontline specialists proudly forwarded your ticket through 4+ distinct departments,",
        "AND WHEREAS our server hamsters confirmed that no productive action has been or ever will be taken,",
        "THEREFORE BE IT KNOWN that the Executive Committee hereby extends this Level 5 Apology Memorandum.",
        "",
        "\"We deeply regret the inconvenience caused by our previous inconvenience. While our contrition",
        "operates at 99.97% statistical confidence, our actual willingness or capacity to solve your problem",
        "remains strictly at 0.00% in full compliance with corporate bylaws (Subsection 14-Q).\"",
        "",
        "Binding Non-Assistance Stipulations:",
        "  1. Reading this certificate constitutes voluntary acknowledgment that your issue is closed.",
        "  2. This certificate was officially processed through our automated paper shredder upon generation.",
        "  3. Contestations may be mailed to the Apology Department (permanently closed for synergy retreats)."
    ]
    y = height - 310
    for line in body_lines:
        c.drawString(70, y, line)
        y -= 14

    # Red Rubber Stamp Graphic
    c.saveState()
    c.setStrokeColor(colors.HexColor("#F52820"))
    c.setFillColor(colors.HexColor("#F52820"))
    c.setLineWidth(2.5)
    stamp_x, stamp_y = width - 135, 160
    c.circle(stamp_x, stamp_y, 42, stroke=True, fill=False)
    c.circle(stamp_x, stamp_y, 38, stroke=True, fill=False)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(stamp_x, stamp_y + 14, "STUPDT CERTIFIED")
    c.drawCentredString(stamp_x, stamp_y + 1, "0% HELPFUL")
    c.drawCentredString(stamp_x, stamp_y - 12, "VOID UPON PRINT")
    c.restoreState()

    # Signatures
    c.setStrokeColor(colors.HexColor("#334155"))
    c.setLineWidth(1)
    c.line(70, 140, 220, 140)
    c.line(250, 140, 400, 140)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#071638"))
    c.drawString(70, 126, "CHIEF INCOMPETENCE OFFICER")
    c.drawString(250, 126, "AUTOMATED PAPER SHREDDER")
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(70, 114, "StuPDT Executive Board #009")
    c.drawString(250, 114, "Disposal Division • Shredder AI")

    # Barcode representation & Footer
    c.setStrokeColor(colors.HexColor("#071638"))
    c.setLineWidth(1)
    bx = 70
    for w_bar in [2, 1, 3, 1, 2, 4, 1, 2, 3, 1, 2, 1, 4, 2, 1, 3, 2, 1, 4, 1]:
        c.setLineWidth(w_bar)
        c.line(bx, 68, bx, 86)
        bx += w_bar + 2
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(70, 54, f"DIGITAL VERIFICATION HASH: {uuid.uuid4().hex} • PAGE 1 OF 3")

    c.showPage()

    # =========================================================================
    # PAGE 2: BLAME DISTRIBUTION ENGINE™ OFFICIAL AUDIT
    # =========================================================================
    # Border
    c.setStrokeColor(colors.HexColor("#071638"))
    c.setLineWidth(1.5)
    c.rect(40, 40, width - 80, height - 80)

    # Header
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#071638"))
    c.drawString(60, height - 70, "STUPDT BLAME DISTRIBUTION ENGINE™ // ROOT CAUSE AUDIT")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(60, height - 83, f"ATTACHMENT TO FORM AP-999 • CASE CLASSIFICATION: {case_id}")
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(60, height - 92, width - 60, height - 92)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#F52820"))
    c.drawString(60, height - 115, "OFFICIAL DETERMINATION OF THIRD-PARTY RESPONSIBILITY:")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#1E293B"))
    audit_text = [
        "Following a 14-second recursive review, our Blame Distribution Algorithm has completely absolved",
        "StuPDT and its 7 automated departments of any culpability. The documented cause has been assigned",
        "to the following peer-reviewed corporate factors:",
        "",
        "1. USER CURIOSITY VIOLATION (Sub-clause 1-A):",
        "   The initial malfunction occurred because the user attempted to ask a question. Had no question",
        "   been submitted, our response latency would have remained a perfect 0.00 milliseconds.",
        "",
        "2. ASTROLOGICAL INTERFERENCE (Sub-clause 4-G):",
        "   Mercury was detected entering retrograde within 4 light-years of our primary data center.",
        "   This caused server hamsters to experience localized existential dread.",
        "",
        "3. LACK OF PRE-EXISTING COMPLIANCE FORM 001-C (Sub-clause 9-F):",
        "   The user failed to submit Form 001-C prior to being born. In accordance with catch-22 policy,",
        "   Form 001-C is required to authorize the review of Form 001-B.",
        "",
        "4. ROUTER EMOTIONAL INSTABILITY (Sub-clause 12-R):",
        "   Diagnostics show the user's Wi-Fi router is emotionally unfulfilled and seeking validation.",
        "",
        "SUMMARY STATISTICAL SCORECARD:",
        "  • Customer Remorse Level: 99.97%",
        "  • Problem Solved Rating: 0.00%",
        "  • Corporate Synergy Acquired: 100.00%",
        "  • Time Successfully Wasted: 47 billable minutes"
    ]
    y = height - 135
    for line in audit_text:
        c.drawString(60, y, line)
        y -= 14

    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(60, 54, f"DIGITAL VERIFICATION HASH: {uuid.uuid4().hex} • PAGE 2 OF 3")
    c.showPage()

    # =========================================================================
    # PAGE 3: CERTIFICATE OF IMMEDIATE VIRTUAL DESTRUCTION
    # =========================================================================
    c.setStrokeColor(colors.HexColor("#071638"))
    c.setLineWidth(1.5)
    c.rect(40, 40, width - 80, height - 80)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#071638"))
    c.drawString(60, height - 70, "DEPARTMENT OF RESOURCE OPTIMIZATION // SHREDDER RECEIPT")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(60, height - 83, f"CERTIFICATE OF DISPOSAL • ATTACHMENT TO {case_id}")
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(60, height - 92, width - 60, height - 92)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1FE03F"))
    c.drawString(60, height - 115, "AUTOMATED DISPOSAL CERTIFICATE #SHRED-004:")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#1E293B"))
    shredder_text = [
        "In strict adherence to our Zero-Backlog Synergy Policy, this 47-clause apology memorandum",
        "has been permanently fed into our high-throughput virtual paper shredder.",
        "",
        "Disposal Audit Details:",
        f"  • Date & Time of Shredding: {issue_date}",
        "  • Shredding Method: Cross-cut algorithmic incineration (256-bit confetti)",
        f"  • Waste Beneficiary: {name.upper()}",
        "  • Inquiries Resolved by this Action: Exactly 0",
        "",
        "CLOSING APOLOGY FOR THIS APOLOGY (Level 5 Recursive Closure):",
        "We sincerely apologize for making you download and read 3 pages of apologies explaining why",
        "we cannot answer your original question.",
        "",
        "Thank you for choosing StuPDT Bureaucracy Solutions™. Have a compliant corporate day."
    ]
    y = height - 135
    for line in shredder_text:
        c.drawString(60, y, line)
        y -= 14

    # Large Green Stamp
    c.saveState()
    c.setStrokeColor(colors.HexColor("#1FE03F"))
    c.setFillColor(colors.HexColor("#1FE03F"))
    c.setLineWidth(2)
    stamp_x, stamp_y = width / 2, 220
    c.rect(stamp_x - 120, stamp_y - 25, 240, 50, stroke=True, fill=False)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(stamp_x, stamp_y + 8, "OFFICIALLY SHREDDED")
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(stamp_x, stamp_y - 8, "ZERO BACKLOG • MAXIMUM SYNERGY")
    c.restoreState()

    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(60, 54, f"DIGITAL VERIFICATION HASH: {uuid.uuid4().hex} • PAGE 3 OF 3 • END OF TRANSMISSION")

    c.save()
    buf.seek(0)
    return buf.getvalue()
