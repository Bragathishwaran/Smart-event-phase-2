from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventCreate, EventOut, EventUpdate

router = APIRouter()


@router.get("", response_model=List[EventOut])
def list_events(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by title or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> List[EventOut]:
    query = db.query(Event)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(Event.title.ilike(term), Event.description.ilike(term))
        )

    if category and category.lower() != "all":
        query = query.filter(Event.category.ilike(category))

    events = (
        query.order_by(Event.event_date.asc()).offset(skip).limit(limit).all()
    )
    return [EventOut.model_validate(e) for e in events]


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)) -> List[str]:
    rows = db.query(Event.category).distinct().all()
    return sorted({row[0] for row in rows if row[0]})


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)) -> EventOut:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventOut.model_validate(event)


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EventOut:
    available = (
        payload.available_tickets
        if payload.available_tickets is not None
        else payload.total_tickets
    )
    if available > payload.total_tickets:
        raise HTTPException(
            status_code=400, detail="available_tickets cannot exceed total_tickets"
        )

    event = Event(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        location=payload.location,
        event_date=payload.event_date,
        ticket_price=payload.ticket_price,
        total_tickets=payload.total_tickets,
        available_tickets=available,
        banner_image=payload.banner_image,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventOut.model_validate(event)


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EventOut:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(event, key, value)

    if event.available_tickets > event.total_tickets:
        raise HTTPException(
            status_code=400, detail="available_tickets cannot exceed total_tickets"
        )

    db.commit()
    db.refresh(event)
    return EventOut.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return None
