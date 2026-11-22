from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


def utc_now() -> datetime:
    """Returns naive UTC datetime compatible with asyncpg TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class VisionScan(Base):
    __tablename__ = "vision_scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String(50), nullable=False)
    target_id = Column(String(200), nullable=True)
    detected_item = Column(String(200), nullable=False)
    category = Column(String(200), nullable=False)
    confidence = Column(String(50), default="100.00%", nullable=False)
    verdict = Column(Text, nullable=False)
    ingredients = Column(Text, nullable=False)
    pro_tip = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
