# SmartEvent Backend

FastAPI backend for the SmartEvent event discovery & ticket booking system.

## Quickstart

```bash
cd smartevent/backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Database

SmartEvent uses **MySQL** by default.

1. Create the database on your MySQL server:
   ```sql
   CREATE DATABASE smartevent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Edit `.env` and set your real credentials:
   ```
   DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/smartevent?charset=utf8mb4
   ```
3. Tables are created automatically on startup (tables use InnoDB + utf8mb4).

> MySQL 8's `caching_sha2_password` auth is supported (installer includes `cryptography`).
> Want SQLite instead? Set `DATABASE_URL=sqlite:///./smartevent.db` in `.env`.

4 sample events are seeded automatically the first time the events table is empty.

## Modules

- Auth (JWT) – `/api/v1/auth`
- Events – `/api/v1/events`
- Bookings – `/api/v1/bookings`
- Tickets / QR – `/api/v1/tickets`
- Notifications – `/api/v1/notifications`
