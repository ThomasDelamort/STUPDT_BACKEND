from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from app.database import Base


def utc_now() -> datetime:
    """Returns naive UTC datetime compatible with asyncpg TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class GlobalTelemetry(Base):
    __tablename__ = "telemetry_metrics"

    id = Column(Integer, primary_key=True, index=True)
    specialists_consulted = Column(Integer, default=1, nullable=False)
    internal_meetings = Column(Integer, default=14, nullable=False)
    minutes_wasted = Column(Integer, default=6, nullable=False)
    user_satisfaction = Column(Integer, default=-18, nullable=False)
    chaos_meter = Column(Integer, default=15, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
