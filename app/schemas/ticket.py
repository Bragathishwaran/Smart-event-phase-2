from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    ticket_code: str
    qr_code_url: Optional[str] = None
    created_at: datetime
