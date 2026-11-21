from typing import Optional
from fastapi import APIRouter, Query, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.telemetry import GlobalTelemetry
from app.services.pdf_service import generate_official_apology_pdf
from app.middleware.security import sanitize_text

router = APIRouter(prefix="/api/apology", tags=["apology"])


@router.get("/download")
async def download_official_apology_pdf(
    name: Optional[str] = Query("Valued Unresolved Citizen", max_length=80, description="Recipient citizen name"),
    reason: Optional[str] = Query("General Inconvenience & Unsolved Inquiries", max_length=150, description="Grievance incident description"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates and downloads an authentic, official 3-page corporate apology certificate PDF
    complete with stamps, barcodes, blame audit, and paper-shredder receipt.
    Includes input sanitization against PDF layout injection.
    """
    clean_name = sanitize_text(name or "Valued Unresolved Citizen", max_length=60)
    clean_reason = sanitize_text(reason or "General Inconvenience & Unsolved Inquiries", max_length=120)

    pdf_bytes = generate_official_apology_pdf(recipient_name=clean_name, case_reason=clean_reason)

    # Bump wasted metrics on server
    try:
        stmt = select(GlobalTelemetry).order_by(desc(GlobalTelemetry.id)).limit(1)
        res = await db.execute(stmt)
        telemetry = res.scalars().first()
        if telemetry:
            telemetry.minutes_wasted += 47
            telemetry.internal_meetings += 2
            await db.commit()
    except Exception:
        pass

    filename = f"StuPDT_Official_Apology_Certificate_Form_AP999.pdf"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/pdf"
    }

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.get("/preview")
async def preview_apology_info():
    """Returns preview metadata for the Apology Certificate modal."""
    return {
        "formNumber": "FORM AP-999-REV-B",
        "title": "Official Certificate of Corporate Regret",
        "authority": "Department of Inaction & Customer Exhaustion",
        "status": "Ready for Immediate Virtual Shredding",
        "totalPages": 3,
        "satisfactionGuaranteed": "0.00%",
        "remorseConfidence": "99.97%"
    }
