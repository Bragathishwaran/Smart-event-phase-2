from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.booking import Booking
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketOut

router = APIRouter()


@router.get("", response_model=List[TicketOut])
def list_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[TicketOut]:
    tickets = (
        db.query(Ticket)
        .join(Booking, Ticket.booking_id == Booking.id)
        .filter(Booking.user_id == current_user.id)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    return [TicketOut.model_validate(t) for t in tickets]


@router.get("/booking/{booking_id}", response_model=List[TicketOut])
def list_tickets_for_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[TicketOut]:
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return [TicketOut.model_validate(t) for t in booking.tickets]


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TicketOut:
    ticket = (
        db.query(Ticket)
        .join(Booking, Ticket.booking_id == Booking.id)
        .filter(Ticket.id == ticket_id, Booking.user_id == current_user.id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketOut.model_validate(ticket)
