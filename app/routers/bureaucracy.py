from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.bureaucracy import BureaucracyFormRequest, BureaucracyFormResponse
from app.models.bureaucracy import BureaucracySubmission
from app.middleware.security import sanitize_text

router = APIRouter(prefix="/api/bureaucracy", tags=["bureaucracy"])


@router.post("/submit", response_model=BureaucracyFormResponse)
async def submit_bureaucracy_form(
    req: BureaucracyFormRequest,
    db: AsyncSession = Depends(get_db)
):
    error_message = (
        "CATCH-22 ERROR: Your request cannot proceed because Form 001-B requires "
        "Form 001-C to be notarized BEFORE you started filling out Form 001."
    )

    # Sanitize user inputs before recording into database
    clean_problem = sanitize_text(req.problem, max_length=500)
    clean_reason = sanitize_text(req.reason, max_length=500)
    clean_notarized_code = sanitize_text(req.notarizedCode, max_length=100)

    # Record submission into PostgreSQL
    try:
        submission = BureaucracySubmission(
            problem=clean_problem,
            reason=clean_reason,
            notarized_code=clean_notarized_code,
            confirmed=req.confirmed,
            status="REJECTED_CATCH_22"
        )
        db.add(submission)
        await db.commit()
    except Exception:
        await db.rollback()

    return BureaucracyFormResponse(
        success=False,
        stamped=False,
        error=error_message
    )
