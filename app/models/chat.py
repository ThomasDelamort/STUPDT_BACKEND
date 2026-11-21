from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


def utc_now() -> datetime:
    """Returns naive UTC datetime compatible with asyncpg TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(String(64), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    ai_reply = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)
