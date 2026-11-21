import json
import base64
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.vision import VisionScan
from app.models.telemetry import GlobalTelemetry
from app.services.vision_service import analyze_vision_payload, SAMPLE_CATALOG
from app.middleware.security import validate_image_magic, sanitize_filename

router = APIRouter(prefix="/api/vision", tags=["vision"])

ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}


class VisionAnalyzeRequest(BaseModel):
    sampleId: Optional[str] = Field(None, max_length=50, description="Optional ID of pre-configured sample asset")
    base64Data: Optional[str] = Field(None, max_length=15000000, description="Base64 encoded image data")
    mimeType: Optional[str] = Field("image/png", max_length=50, description="MIME type of the image")
    filename: Optional[str] = Field(None, max_length=120, description="Uploaded file name")


class VisionAnalyzeResponse(BaseModel):
    scanId: Optional[int] = None
    detectedItem: str
    category: str
    confidence: str = "100.00%"
    verdict: str
    ingredients: List[str]
    proTip: str


class VisionSampleItem(BaseModel):
    id: str
    label: str
    iconType: str
    scanText: str


@router.get("/samples", response_model=List[VisionSampleItem])
async def get_vision_samples():
    """Returns certified sample catalog for the Vision AI scanner."""
    return [
        {
            "id": "rock",
            "label": "Photo of a Rock",
            "iconType": "mountain",
            "scanText": "Analyzing molecular geology across 14 departments..."
        },
        {
            "id": "spaghetti",
            "label": "Plate of Spaghetti",
            "iconType": "utensils",
            "scanText": "Deconstructing culinary carbohydrate topology..."
        },
        {
            "id": "water",
            "label": "Glass of Water",
            "iconType": "glass",
            "scanText": "Measuring aqueous wetness and hydration friction..."
        }
    ]


@router.post("/analyze", response_model=VisionAnalyzeResponse)
async def analyze_image_endpoint(
    req: VisionAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Performs server-side AI tautological inspection of user-uploaded images or sample assets.
    Records audit entry in PostgreSQL. Includes MIME verification and magic byte validation.
    """
    if not req.sampleId and not req.base64Data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either sampleId or base64Data image payload."
        )

    # Sanitize filename
    clean_filename = sanitize_filename(req.filename) if req.filename else None

    # If user uploaded base64 data, validate MIME type and magic bytes
    if req.base64Data:
        mime = (req.mimeType or "image/png").lower().strip()
        if mime not in ALLOWED_IMAGE_MIMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format: '{mime}'. Only PNG, JPEG, WEBP, and GIF are allowed."
            )
        try:
            raw_bytes = base64.b64decode(req.base64Data[:1024])
            if not validate_image_magic(raw_bytes, mime):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Corrupted or invalid image binary signature. Executable or script files are strictly rejected."
                )
        except Exception as exc:
            if isinstance(exc, HTTPException):
                raise exc
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed base64 image data."
            )

    analysis = await analyze_vision_payload(
        sample_id=req.sampleId,
        base64_data=req.base64Data,
        mime_type=req.mimeType,
        filename=clean_filename
    )

    # Persist scan audit in PostgreSQL
    scan_record = VisionScan(
        scan_type="sample" if req.sampleId else "upload",
        target_id=req.sampleId or clean_filename or "uploaded_image",
        detected_item=analysis["detectedItem"],
        category=analysis["category"],
        confidence=analysis.get("confidence", "100.00%"),
        verdict=analysis["verdict"],
        ingredients=json.dumps(analysis.get("ingredients", [])),
        pro_tip=analysis.get("proTip", "")
    )
    db.add(scan_record)

    # Bump telemetry wasted metrics on server
    try:
        stmt = select(GlobalTelemetry).order_by(desc(GlobalTelemetry.id)).limit(1)
        telemetry_result = await db.execute(stmt)
        telemetry = telemetry_result.scalars().first()
        if telemetry:
            telemetry.specialists_consulted += 1
            telemetry.minutes_wasted += 3
    except Exception:
        pass

    await db.commit()
    await db.refresh(scan_record)

    return VisionAnalyzeResponse(
        scanId=scan_record.id,
        detectedItem=analysis["detectedItem"],
        category=analysis["category"],
        confidence=analysis.get("confidence", "100.00%"),
        verdict=analysis["verdict"],
        ingredients=analysis.get("ingredients", []),
        proTip=analysis.get("proTip", "")
    )


@router.get("/history")
async def get_vision_history(db: AsyncSession = Depends(get_db)):
    """Returns recent server-certified vision audits."""
    stmt = select(VisionScan).order_by(desc(VisionScan.id)).limit(10)
    result = await db.execute(stmt)
    scans = result.scalars().all()
    return [
        {
            "id": s.id,
            "scanType": s.scan_type,
            "targetId": s.target_id,
            "detectedItem": s.detected_item,
            "category": s.category,
            "confidence": s.confidence,
            "verdict": s.verdict,
            "ingredients": json.loads(s.ingredients) if s.ingredients.startswith("[") else [s.ingredients],
            "proTip": s.pro_tip,
            "createdAt": s.created_at.isoformat()
        }
        for s in scans
    ]
