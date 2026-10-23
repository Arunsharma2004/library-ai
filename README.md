# LibraX — Smart Library Management System

A full-stack library management web app with AI built in. Staff manage books, members and
loans. Visitors can join the library, browse the catalog and get AI help finding their next read.

**Stack:** FastAPI · SQLAlchemy · Pydantic · SQLite (PostgreSQL-ready) · vanilla HTML/CSS/JavaScript · Google Gemini

> **Live demo:** <https://librax-6t46.onrender.com>
> The free server sleeps when idle, so the first visit after a quiet period can take about a minute to load.

## Features

**Library management (staff)**
- Add, edit, delete and view books, with search and filters (title, author, ISBN, category, availability)
- Manage library members
- Issue and return books with clear rules: only active members can borrow, a copy must be available, and a member can't hold the same book twice. Loans are due after 14 days
- Full borrowing history, with overdue detection
- Books and members with borrowing history can't be deleted, so records are never lost

**AI features**
- **Find a book:** answer a few questions (mood, interests, length) and get recommendations from the library's own catalog, each with a reason
- **Ask the librarian:** a chat assistant that understands natural-language questions and answers using the real catalog
- **AI book descriptions:** staff can generate a short description for a book and review it before saving
- The AI only recommends books that exist in the library, and any book it invents is dropped

**Visitors and members**
- A public **Join the library** form creates a *pending* member. Staff approve them before they can borrow
- After joining, a visitor can browse books and use the AI, with usage limits
- A **My account** page shows the member's status (pending or approved) and their own loans

**Security**
- Staff sign in with a password stored as a salted PBKDF2 hash (600,000 iterations)
- The login is a signed, HttpOnly cookie
- Every staff route is protected on the server, and visitors get `403` on staff routes, whatever the menu shows
- Uploaded or typed text is displayed as text, never as HTML
- The AI key and other secrets live in environment variables, never in the code
- In production mode the app refuses to start with an unsafe secret key
- Rate limits: 5 join requests per hour per IP, 25 AI requests per hour per visitor, and a daily cap on AI use across the whole site (staff are not limited)

## How it is organized

```
backend/app/
  models/      database tables (SQLAlchemy)
  schemas/     request and response shapes (Pydantic)
  services/    the business rules (no web code in here)
  routers/     the HTTP endpoints (only translate between HTTP and services)
  ai/          one small wrapper around the Gemini API
  scripts/     create_staff, seed_demo
backend/tests/ automated tests (pytest, in-memory database)
frontend/      HTML, CSS and JavaScript pages (no framework)
```

Each layer has one job. Routers handle HTTP, services hold the rules (and raise clear errors), models talk
to the database. The AI provider can be switched by editing only `ai/client.py`.

## Run it locally

You need Python 3.12 or newer (developed and tested on 3.14).

```powershell
git clone https://github.com/Arunsharma2004/library-ai.git
cd library-ai
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
Copy-Item .env.example .env
```

Open `backend\.env` and fill in your values (see Settings below). At minimum, set `GEMINI_API_KEY`
(a free key from [Google AI Studio](https://aistudio.google.com)).

Create a staff account and add some sample books:

```powershell
python -m app.scripts.create_staff librarian
python -m app.scripts.seed_demo
```

Start the app, then open <http://127.0.0.1:8000>:

```powershell
uvicorn app.main:app --reload
```

Interactive API docs are at <http://127.0.0.1:8000/docs>.

## Settings

All settings are environment variables (or lines in `backend/.env`).

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development` (default) or `production` |
| `SECRET_KEY` | Signs the login cookie. In production it must be random and at least 32 characters |
| `COOKIE_SECURE` | Send cookies over HTTPS only. On by default in production |
| `DATABASE_URL` | Empty = local SQLite file. For PostgreSQL: `postgresql://user:password@host:5432/library` |
| `GEMINI_API_KEY` | Key for the AI features |
| `GEMINI_MODEL` | Gemini model name (default `gemini-3.5-flash-lite`) |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | Optional. Creates the first staff account at startup, only if no staff exist yet |

Create a strong secret key with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Tests

```powershell
cd backend
pytest -q
```

119 tests cover the books, members and borrowing rules, login and access rules (including what visitors may and
may not do), rate limits, the AI features (with the AI faked, so tests are fast and free), and the production safety checks.

## API overview

| Area | Endpoints | Who |
|---|---|---|
| Auth | `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`, `GET /api/auth/session` | anyone / signed in |
| Books | `GET /api/books`, `GET /api/books/{id}` | staff and visitors |
| Books | `POST /api/books`, `PATCH /api/books/{id}`, `DELETE /api/books/{id}` | staff |
| Members | create, list, edit and delete under `/api/members` | staff |
| Borrowing | `POST /api/borrows/issue`, `POST /api/borrows/{id}/return`, `GET /api/borrows` | staff |
| AI | `POST /api/ai/recommendations`, `POST /api/ai/chat` | staff and visitors (limited) |
| AI | `POST /api/ai/describe` | staff |
| Join | `POST /api/public/join` | anyone (rate limited) |
| My account | `GET /api/my/account` | the member linked to the browser |
| Health | `GET /api/health` | anyone |

## Known limitations

These are deliberate trade-offs for a small project, and good next steps:

- **Visitors are not real accounts.** "My account" works through a signed cookie set when someone joins, so it only works in
  that browser. Someone who joins with an email that already exists is not linked to it. Real member logins would
  need passwords and email verification.
- **Rate limits live in memory,** so they reset when the server restarts and are per server process. A larger deployment would use Redis.
- **No login rate limiting and no password reset** for staff. Staff accounts are created by an administrator.
- **The AI sees at most 200 books** of the catalog per request.
- **The free Gemini tier has quotas.** When they run out, the AI features show a friendly "try again later" message and the rest of the app keeps working. Check Google's terms for how free-tier data may be used.
- Tests run on SQLite. The code is written to be PostgreSQL-ready (SQLAlchemy, no SQLite-only features), but PostgreSQL is not part of the automated tests.
- Changing the structure of an existing table (for example adding a column) needs a migration tool such as Alembic, which is not set up yet.

## Roadmap

- A small Git-like version history for library data (init, stage, commit, log, restore, with AI-written commit messages)
- Real member accounts
- Database migrations with Alembic