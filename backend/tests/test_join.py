import pytest

from app.routers.public import join_limiter


@pytest.fixture(autouse=True)
def fresh_limiter():
    """Every test starts with an empty rate limiter."""
    join_limiter.reset()


def join(client, name="Ravi Kumar", email="ravi@example.com", phone=None):
    return client.post("/api/public/join", json={"name": name, "email": email, "phone": phone})


def find_member(client, email):
    members = client.get("/api/members").json()
    return next((m for m in members if m["email"] == email), None)


def test_join_creates_a_pending_member(client):
    response = join(client)

    assert response.status_code == 201
    member = find_member(client, "ravi@example.com")
    assert member is not None
    assert member["is_active"] is False


def test_join_needs_no_login(raw_client):
    assert join(raw_client).status_code == 201


def test_duplicate_email_creates_nothing_and_reveals_nothing(client):
    join(client)

    again = join(client, name="Someone Else")

    assert again.status_code == 201
    assert len([m for m in client.get("/api/members").json() if m["email"] == "ravi@example.com"]) == 1
    assert find_member(client, "ravi@example.com")["name"] == "Ravi Kumar"


def test_duplicate_email_ignores_upper_and_lower_case(client):
    join(client, email="ravi@example.com")
    join(client, email="RAVI@Example.com")

    assert len(client.get("/api/members").json()) == 1


def test_invalid_email_is_rejected(client):
    assert join(client, email="not-an-email").status_code == 422


def test_name_is_required(client):
    assert join(client, name="   ").status_code == 422


def test_too_many_requests_are_blocked(client):
    for number in range(5):
        assert join(client, email=f"person{number}@example.com").status_code == 201

    blocked = join(client, email="person6@example.com")

    assert blocked.status_code == 429
    assert find_member(client, "person6@example.com") is None