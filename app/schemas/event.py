from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., description="Music / Tech / Sports / Business")
    location: Optional[str] = None
    event_date: datetime
    ticket_price: float = Field(..., ge=0)
    total_tickets: int = Field(..., ge=0)
    banner_image: Optional[str] = None


class EventCreate(EventBase):
    available_tickets: Optional[int] = Field(None, ge=0)


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None
    ticket_price: Optional[float] = Field(None, ge=0)
    total_tickets: Optional[int] = Field(None, ge=0)
    available_tickets: Optional[int] = Field(None, ge=0)
    banner_image: Optional[str] = None


class EventOut(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    available_tickets: int
    is_sold_out: bool
    created_at: datetime
