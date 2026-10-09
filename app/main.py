import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models import Event  # noqa: F401  (ensures models are registered)

# Import all models so SQLAlchemy knows about them before create_all
from app.models import Booking, Notification, Ticket, User  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_events() -> None:
    db = SessionLocal()
    try:
        if db.query(Event).count() > 0:
            return

        now = datetime.now(timezone.utc)
        sample_events = [
            {
                "title": "Neon Nights Music Festival",
                "description": "An electrifying night of live electronic and indie music.",
                "category": "Music",
                "location": "Madison Square Garden, NYC",
                "event_date": now + timedelta(days=14),
                "ticket_price": 79.99,
                "total_tickets": 500,
                "banner_image": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200",
            },
            {
                "title": "AI & Machine Learning Summit",
                "description": "Industry leaders discuss the future of applied AI.",
                "category": "Tech",
                "location": "Moscone Center, San Francisco",
                "event_date": now + timedelta(days=30),
                "ticket_price": 149.00,
                "total_tickets": 300,
                "banner_image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200",
            },
            {
                "title": "City Marathon Championship",
                "description": "Cheer on elite runners at the annual city marathon.",
                "category": "Sports",
                "location": "Central Park, NYC",
                "event_date": now + timedelta(days=7),
                "ticket_price": 25.00,
                "total_tickets": 2000,
                "banner_image": "https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=1200",
            },
            {
                "title": "Startup Growth Conference",
                "description": "Networking and workshops for founders and investors.",
                "category": "Business",
                "location": "Austin Convention Center, TX",
                "event_date": now + timedelta(days=45),
                "ticket_price": 199.00,
                "total_tickets": 150,
                "banner_image": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=1200",
            },
        ]

        for data in sample_events:
            data["available_tickets"] = data["total_tickets"]
            db.add(Event(**data))
        db.commit()
    finally:
        db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    os.makedirs(settings.QRCODE_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.on_event("startup")
    def on_startup() -> None:
        create_tables()
        seed_events()

    @app.get("/", tags=["Health"])
    def root() -> dict:
        return {"message": "SmartEvent API", "docs": "/docs"}

    @app.get("/health", tags=["Health"])
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
