import pytest

from app.services import user_service
from app.services.errors import BusinessRuleError, DuplicateError
from app.services.security import verify_password

PASSWORD = "correct-horse-1"


def add_staff(session_factory, username="librarian", password=PASSWORD):
    db = session_factory()
    try:
        user_service.create_user(db, username, password)
    finally:
        db.close()


def login(client, username="librarian", password=PASSWORD):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_api_requires_login(raw_client):
    for path in ["/api/books", "/api/members", "/api/borrows"]:
        assert raw_client.get(path).status_code == 401


def test_health_check_is_public(raw_client):
    assert raw_client.get("/api/health").status_code == 200


def test_login_with_the_correct_password(raw_client, session_factory):
    add_staff(session_factory)

    response = login(raw_client)

    assert response.status_code == 200
    assert response.json()["username"] == "librarian"
    # The cookie from the login is now sent automatically with every request.
    assert raw_client.get("/api/books").status_code == 200


def test_wrong_password_is_rejected(raw_client, session_factory):
    add_staff(session_factory)

    response = login(raw_client, password="wrong-password")

    assert response.status_code == 401
    assert raw_client.get("/api/books").status_code == 401


def test_unknown_user_gets_the_same_error(raw_client, session_factory):
    add_staff(session_factory)

    wrong_password = login(raw_client, password="wrong-password")
    unknown_user = login(raw_client, username="nobody")

    assert unknown_user.status_code == 401
    assert unknown_user.json() == wrong_password.json()  # reveals nothing about usernames


def test_username_is_not_case_sensitive(raw_client, session_factory):
    add_staff(session_factory)

    assert login(raw_client, username="LIBRARIAN").status_code == 200


def test_logout_ends_the_session(raw_client, session_factory):
    add_staff(session_factory)
    login(raw_client)

    response = raw_client.post("/api/auth/logout")

    assert response.status_code == 204
    assert raw_client.get("/api/books").status_code == 401


def test_me_returns_the_signed_in_user(raw_client, session_factory):
    add_staff(session_factory)
    login(raw_client)

    response = raw_client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["username"] == "librarian"


def test_issued_by_records_the_staff_member(raw_client, session_factory):
    add_staff(session_factory)
    login(raw_client)
    book = raw_client.post("/api/books", json={"title": "Dune", "author": "Frank Herbert"}).json()
    member = raw_client.post(
        "/api/members", json={"name": "Asha Rao", "email": "asha@example.com"}
    ).json()

    loan = raw_client.post(
        "/api/borrows/issue", json={"book_id": book["id"], "member_id": member["id"]}
    ).json()

    assert loan["issued_by"] == "librarian"


def test_password_is_stored_hashed(session_factory):
    db = session_factory()
    try:
        user = user_service.create_user(db, "librarian", PASSWORD)

        assert user.password_hash != PASSWORD
        assert verify_password(PASSWORD, user.password_hash)
        assert not verify_password("wrong-password", user.password_hash)
    finally:
        db.close()


def test_short_password_is_rejected(session_factory):
    db = session_factory()
    try:
        with pytest.raises(BusinessRuleError):
            user_service.create_user(db, "librarian", "short")
    finally:
        db.close()


def test_duplicate_username_is_rejected(session_factory):
    add_staff(session_factory)
    db = session_factory()
    try:
        with pytest.raises(DuplicateError):
            user_service.create_user(db, "Librarian", PASSWORD)  # same name, different case
    finally:
        db.close()