from app.ai.client import AIError

BOOK = {
    "title": "Dune",
    "author": "Frank Herbert",
    "category": "Science Fiction",
    "published_year": 1965,
}


def fake_ai(monkeypatch, reply):
    """Replaces the real AI with one that gives a fixed reply and remembers the prompt."""
    seen = {}

    def fake(prompt, system=None):
        seen["prompt"] = prompt
        return reply

    monkeypatch.setattr("app.ai.client.ask", fake)
    return seen


def test_returns_a_description(client, monkeypatch):
    fake_ai(monkeypatch, "A desert planet epic.")

    response = client.post("/api/ai/describe", json=BOOK)

    assert response.status_code == 200
    assert response.json()["description"] == "A desert planet epic."


def test_the_book_details_are_sent_to_the_ai(client, monkeypatch):
    seen = fake_ai(monkeypatch, "Anything.")

    client.post("/api/ai/describe", json=BOOK)

    assert "Dune" in seen["prompt"]
    assert "Frank Herbert" in seen["prompt"]
    assert "Science Fiction" in seen["prompt"]


def test_overlong_reply_is_cut(client, monkeypatch):
    fake_ai(monkeypatch, "x" * 5000)

    response = client.post("/api/ai/describe", json=BOOK)

    assert len(response.json()["description"]) == 1000


def test_ai_failure_gives_503(client, monkeypatch):
    def broken(prompt, system=None):
        raise AIError("The AI service could not answer right now. Please try again.")

    monkeypatch.setattr("app.ai.client.ask", broken)

    assert client.post("/api/ai/describe", json=BOOK).status_code == 503


def test_requires_login(raw_client):
    assert raw_client.post("/api/ai/describe", json=BOOK).status_code == 401


def test_title_and_author_are_required(client):
    assert client.post("/api/ai/describe", json={"title": "Dune"}).status_code == 422
    assert client.post("/api/ai/describe", json={"title": "", "author": "x"}).status_code == 422