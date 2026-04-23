from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from app.extensions import Base


class PoemRequest(Base):
    __tablename__ = "poem_requests"

    id = Column(Integer, primary_key=True)
    theme = Column(String(150), nullable=False)
    mood = Column(String(20), nullable=False)
    stanza_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
