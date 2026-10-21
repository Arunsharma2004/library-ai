MEMBER = {
    "name": "Asha Rao",
    "email": "asha@example.com",
    "phone": "9876543210",
}


def make_member(client, **changes):
    """Helper: creates a member (Asha by default) and returns it as a dictionary."""
    response = client.post("/api/members", json={**MEMBER, **changes})
    assert response.status_code == 201
    return response.json()


# ---------- Create ----------
def test_create_member(client):
    response = client.post("/api/members", json=MEMBER)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Asha Rao"
    assert data["is_active"] is True  # new members start active


def test_email_is_stored_in_lowercase(client):
    member = make_member(client, email="Asha@Example.COM")

    assert member["email"] == "asha@example.com"


def test_duplicate_email_is_rejected_even_with_different_case(client):
    make_member(client)

    response = client.post("/api/members", json={**MEMBER, "email": "ASHA@example.com"})

    assert response.status_code == 409


def test_invalid_email_is_rejected(client):
    response = client.post("/api/members", json={**MEMBER, "email": "not-an-email"})

    assert response.status_code == 422


# ---------- Read, search and filter ----------
def test_list_and_search_members(client):
    make_member(client)
    make_member(client, name="Ravi Kumar", email="ravi@example.com")

    assert len(client.get("/api/members").json()) == 2

    results = client.get("/api/members", params={"search": "RAVI"}).json()
    assert len(results) == 1
    assert results[0]["name"] == "Ravi Kumar"


def test_active_only_filter(client):
    make_member(client)
    inactive = make_member(client, name="Ravi Kumar", email="ravi@example.com")
    client.patch(f"/api/members/{inactive['id']}", json={"is_active": False})

    results = client.get("/api/members", params={"active_only": True}).json()

    assert len(results) == 1
    assert results[0]["name"] == "Asha Rao"


def test_get_missing_member_returns_404(client):
    response = client.get("/api/members/999")

    assert response.status_code == 404


# ---------- Update ----------
def test_update_changes_only_the_sent_fields(client):
    member = make_member(client)

    response = client.patch(f"/api/members/{member['id']}", json={"phone": "1112223333"})

    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "1112223333"
    assert data["name"] == "Asha Rao"  # untouched


def test_update_to_an_existing_email_is_rejected(client):
    make_member(client)
    other = make_member(client, name="Ravi Kumar", email="ravi@example.com")

    response = client.patch(f"/api/members/{other['id']}", json={"email": MEMBER["email"]})

    assert response.status_code == 409


def test_update_missing_member_returns_404(client):
    response = client.patch("/api/members/999", json={"name": "Nobody"})

    assert response.status_code == 404


# ---------- Delete ----------
def test_delete_member(client):
    member = make_member(client)

    response = client.delete(f"/api/members/{member['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/members/{member['id']}").status_code == 404


def test_delete_missing_member_returns_404(client):
    response = client.delete("/api/members/999")

    assert response.status_code == 404