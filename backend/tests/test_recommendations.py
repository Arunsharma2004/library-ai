from app.ai.client import AIError

ANSWERS = {"mood": "Fiction", "interests": "space", "length": "any"}


def make_book(client, title, isbn):
    response = client.post(
        "/api/books", json={"title": title, "author": "Some Author", "isbn": isbn}
    )
    assert response.status_code == 201
    return response.json()


def fake_ai(monkeypatch, reply):
    """Replaces the real AI with one that always gives the same reply."""
    monkeypatch.setattr("app.ai.client.ask", lambda prompt, system=None: reply)


def test_returns_the_books_the_ai_picked(client, monkeypatch):
    first = make_book(client, "Dune", "111")
    second = make_book(client, "Emma", "222")
    fake_ai(monkeypatch, f"{first['id']}|Great desert epic\n{second['id']}|A classic")

    response = client.post("/api/ai/recommendations", json=ANSWERS)

    assert response.status_code == 200
    items = response.json()["recommendations"]
    assert [item["book"]["title"] for item in items] == ["Dune", "Emma"]
    assert items[0]["reason"] == "Great desert epic"


def test_ignores_books_the_ai_invented(client, monkeypatch):
    real = make_book(client, "Dune", "111")
    fake_ai(monkeypatch, f"999|A book that does not exist\n{real['id']}|A real one")

    items = client.post("/api/ai/recommendations", json=ANSWERS).json()["recommendations"]

    assert [item["book"]["title"] for item in items] == ["Dune"]


def test_survives_a_messy_reply(client, monkeypatch):
    real = make_book(client, "Dune", "111")
    fake_ai(monkeypatch, f"Sure! Here you go:\n{real['id']} | fits well\nnot a pick line\n")

    items = client.post("/api/ai/recommendations", json=ANSWERS).json()["recommendations"]

    assert len(items) == 1
    assert items[0]["reason"] == "fits well"


def test_none_reply_gives_an_empty_list(client, monkeypatch):
    make_book(client, "Dune", "111")
    fake_ai(monkeypatch, "NONE")

    response = client.post("/api/ai/recommendations", json=ANSWERS)

    assert response.status_code == 200
    assert response.json()["recommendations"] == []


def test_never_returns_more_than_five(client, monkeypatch):
    books = [make_book(client, f"Book {n}", f"isbn-{n}") for n in range(7)]
    fake_ai(monkeypatch, "\n".join(f"{book['id']}|reason" for book in books))

    items = client.post("/api/ai/recommendations", json=ANSWERS).json()["recommendations"]

    assert len(items) == 5


def test_empty_library_does_not_call_the_ai(client, monkeypatch):
    def must_not_be_called(prompt, system=None):
        raise AssertionError("the AI should not be called for an empty library")

    monkeypatch.setattr("app.ai.client.ask", must_not_be_called)

    response = client.post("/api/ai/recommendations", json=ANSWERS)

    assert response.status_code == 200
    assert response.json()["recommendations"] == []


def test_ai_failure_gives_503(client, monkeypatch):
    make_book(client, "Dune", "111")

    def broken(prompt, system=None):
        raise AIError("The AI service could not answer right now. Please try again.")

    monkeypatch.setattr("app.ai.client.ask", broken)

    response = client.post("/api/ai/recommendations", json=ANSWERS)

    assert response.status_code == 503


def test_requires_login(raw_client):
    assert raw_client.post("/api/ai/recommendations", json=ANSWERS).status_code == 401


def test_needs_interests(client):
    response = client.post("/api/ai/recommendations", json={"mood": "Fiction", "interests": ""})

    assert response.status_code == 422