from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base


def utc_now() -> datetime:
    """Returns naive UTC datetime compatible with asyncpg TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BureaucracySubmission(Base):
    __tablename__ = "bureaucracy_submissions"

    id = Column(Integer, primary_key=True, index=True)
    problem = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    notarized_code = Column(String(256), nullable=False)
    confirmed = Column(Boolean, default=False)
    status = Column(String(64), default="REJECTED_CATCH_22")
    created_at = Column(DateTime, default=utc_now)
