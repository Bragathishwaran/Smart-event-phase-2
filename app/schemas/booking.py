from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.event import EventOut
from app.schemas.ticket import TicketOut


class BookingCreate(BaseModel):
    event_id: int
    ticket_quantity: int = Field(1, ge=1, le=10)


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    event_id: int
    ticket_quantity: int
    total_price: float
    booking_status: str
    created_at: datetime
    event: EventOut
    tickets: List[TicketOut] = []
