from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), index=True, nullable=False)
    location = Column(String(255), nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=False)
    ticket_price = Column(Float, nullable=False, default=0.0)
    total_tickets = Column(Integer, nullable=False, default=0)
    available_tickets = Column(Integer, nullable=False, default=0)
    banner_image = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    bookings = relationship(
        "Booking", back_populates="event", cascade="all, delete-orphan"
    )

    @property
    def is_sold_out(self) -> bool:
        return self.available_tickets <= 0
