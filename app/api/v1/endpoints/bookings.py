from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.notification_service import create_booking_confirmation
from app.services.qr_service import generate_qr_code, generate_ticket_code

router = APIRouter()


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookingOut:
    event = db.query(Event).filter(Event.id == payload.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.available_tickets <= 0:
        raise HTTPException(status_code=400, detail="Event is sold out")

    if payload.ticket_quantity > event.available_tickets:
        raise HTTPException(
            status_code=400,
            detail=f"Only {event.available_tickets} ticket(s) remaining",
        )

    total_price = round(event.ticket_price * payload.ticket_quantity, 2)

    booking = Booking(
        user_id=current_user.id,
        event_id=event.id,
        ticket_quantity=payload.ticket_quantity,
        total_price=total_price,
        booking_status=BookingStatus.CONFIRMED,
    )

    event.available_tickets -= payload.ticket_quantity

    db.add(booking)
    db.flush()

    for _ in range(payload.ticket_quantity):
        code = generate_ticket_code()
        qr_url = generate_qr_code(
            ticket_code=code,
            extra_data=f"booking_id={booking.id}&event_id={event.id}",
        )
        db.add(Ticket(booking_id=booking.id, ticket_code=code, qr_code_url=qr_url))

    create_booking_confirmation(
        db,
        user_id=current_user.id,
        event_title=event.title,
        quantity=payload.ticket_quantity,
        total_price=total_price,
        booking_id=booking.id,
    )

    db.commit()
    db.refresh(booking)
    return BookingOut.model_validate(booking)


@router.get("", response_model=List[BookingOut])
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[BookingOut]:
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return [BookingOut.model_validate(b) for b in bookings]


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookingOut:
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingOut.model_validate(booking)


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookingOut:
    booking = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.booking_status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking already cancelled")

    booking.booking_status = BookingStatus.CANCELLED
    if booking.event:
        booking.event.available_tickets += booking.ticket_quantity

    db.commit()
    db.refresh(booking)
    return BookingOut.model_validate(booking)
