from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.telemetry import TelemetryMetrics
from app.models.telemetry import GlobalTelemetry

router = APIRouter(prefix="/api", tags=["telemetry"])


@router.get("/metrics", response_model=TelemetryMetrics)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    stmt = select(GlobalTelemetry).order_by(GlobalTelemetry.id.asc()).limit(1)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if not record:
        record = GlobalTelemetry(
            specialists_consulted=1,
            internal_meetings=14,
            minutes_wasted=6,
            user_satisfaction=-18,
            chaos_meter=15
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)

    return TelemetryMetrics(
        specialistsConsulted=record.specialists_consulted,
        internalMeetings=record.internal_meetings,
        minutesWasted=record.minutes_wasted,
        userSatisfaction=record.user_satisfaction,
        chaosMeter=record.chaos_meter
    )


@router.post("/metrics", response_model=TelemetryMetrics)
async def update_metrics(metrics: TelemetryMetrics, db: AsyncSession = Depends(get_db)):
    stmt = select(GlobalTelemetry).order_by(GlobalTelemetry.id.asc()).limit(1)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if not record:
        record = GlobalTelemetry()
        db.add(record)

    record.specialists_consulted = metrics.specialistsConsulted
    record.internal_meetings = metrics.internalMeetings
    record.minutes_wasted = metrics.minutesWasted
    record.user_satisfaction = metrics.userSatisfaction
    record.chaos_meter = metrics.chaosMeter

    await db.commit()
    await db.refresh(record)

    return metrics
