from fastapi import APIRouter

from app.api.v1.endpoints import auth, bookings, events, notifications, tickets

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)
