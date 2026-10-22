import pytest

from app.dependencies import site_ai_limiter
from app.models.book import Book
from app.models.user import User
from app.services.security import hash_password


# ---------- Helpers ----------
def become_visitor(client):
    response = client.post(
        "/api/public/join", json={"name": "Ravi Kumar", "email": "ravi@example.com"}
    )
    assert response.status_code == 201


def sign_in_staff(client, session_factory):
    with session_factory() as db:
        db.add(User(username="anna", password_hash=hash_password("password123")))
        db.commit()
    response = client.post("/api/auth/login", json={"username": "anna", "password": "password123"})
    assert response.status_code == 200


def fake_ai(monkeypatch):
    monkeypatch.setattr("app.ai.client.ask", lambda prompt, system=None: "Hello there")


def chat(client):
    return client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": "hi"}]})


# ---------- Who am I? ----------
def test_session_needs_a_session(raw_client):
    assert raw_client.get("/api/auth/session").status_code == 401


def test_joining_makes_you_a_visitor(raw_client):
    become_visitor(raw_client)

    assert raw_client.get("/api/auth/session").json() == {"role": "visitor", "username": None}


def test_staff_login_replaces_the_visitor_role(raw_client, session_factory):
    become_visitor(raw_client)
    sign_in_staff(raw_client, session_factory)

    assert raw_client.get("/api/auth/session").json() == {"role": "staff", "username": "anna"}


def test_logout_ends_a_visitor_session(raw_client):
    become_visitor(raw_client)

    assert raw_client.post("/api/auth/logout").status_code == 204
    assert raw_client.get("/api/auth/session").status_code == 401


# ---------- What a visitor may do ----------
def test_nobody_signed_in_still_gets_401(raw_client):
    assert raw_client.get("/api/books").status_code == 401


def test_visitor_can_read_books(raw_client, session_factory):
    with session_factory() as db:
        db.add(Book(title="Dune", author="Frank Herbert", total_copies=1, available_copies=1))
        db.commit()
    become_visitor(raw_client)

    listing = raw_client.get("/api/books")

    assert listing.status_code == 200
    assert [book["title"] for book in listing.json()] == ["Dune"]
    assert raw_client.get("/api/books/1").status_code == 200


def test_visitor_can_use_the_recommender(raw_client):
    become_visitor(raw_client)

    # An empty body is invalid (422), which proves the visitor got past the access
    # check: a refused visitor would have received 401 or 403 instead.
    assert raw_client.post("/api/ai/recommendations", json={}).status_code == 422


def test_visitor_can_use_the_chat(raw_client, monkeypatch):
    fake_ai(monkeypatch)
    become_visitor(raw_client)

    assert chat(raw_client).status_code == 200


# ---------- What a visitor may NOT do ----------
STAFF_ONLY = [
    ("get", "/api/members"),
    ("get", "/api/borrows"),
    ("post", "/api/books"),
    ("patch", "/api/books/1"),
    ("delete", "/api/books/1"),
    ("post", "/api/ai/describe"),
]


@pytest.mark.parametrize("method,url", STAFF_ONLY)
def test_visitor_is_refused_on_staff_routes(raw_client, method, url):
    become_visitor(raw_client)

    assert getattr(raw_client, method)(url).status_code == 403


# ---------- AI limits ----------
def test_visitor_ai_use_is_limited_per_hour(raw_client, monkeypatch):
    fake_ai(monkeypatch)
    become_visitor(raw_client)

    for _ in range(25):
        assert chat(raw_client).status_code == 200

    blocked = chat(raw_client)
    assert blocked.status_code == 429
    assert "this hour" in blocked.json()["detail"]


def test_whole_site_has_a_daily_ai_cap(raw_client, monkeypatch):
    fake_ai(monkeypatch)
    monkeypatch.setattr(site_ai_limiter, "max_requests", 2)
    become_visitor(raw_client)

    assert chat(raw_client).status_code == 200
    assert chat(raw_client).status_code == 200
    blocked = chat(raw_client)

    assert blocked.status_code == 429
    assert "tomorrow" in blocked.json()["detail"]


def test_staff_are_never_limited(raw_client, session_factory, monkeypatch):
    fake_ai(monkeypatch)
    monkeypatch.setattr(site_ai_limiter, "max_requests", 0)  # visitors would be blocked at once
    sign_in_staff(raw_client, session_factory)

    for _ in range(12):
        assert chat(raw_client).status_code == 200