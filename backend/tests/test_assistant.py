from app.ai.client import AIError


def make_book(client, title, isbn):
    response = client.post(
        "/api/books", json={"title": title, "author": "Some Author", "isbn": isbn}
    )
    assert response.status_code == 201
    return response.json()


def say(client, text="Suggest something"):
    return client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": text}]})


def fake_ai(monkeypatch, reply):
    """Replaces the real AI with one that gives a fixed reply and remembers the prompt."""
    seen = {}

    def fake(prompt, system=None):
        seen["prompt"] = prompt
        return reply

    monkeypatch.setattr("app.ai.client.ask", fake)
    return seen


def test_returns_the_reply_and_the_chosen_books(client, monkeypatch):
    book = make_book(client, "Dune", "111")
    fake_ai(monkeypatch, f"Try Dune, it is a classic.\nBOOKS: {book['id']}")

    response = say(client)

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Try Dune, it is a classic."  # the BOOKS line is removed
    assert [b["title"] for b in data["books"]] == ["Dune"]


def test_ignores_books_the_ai_invented(client, monkeypatch):
    real = make_book(client, "Dune", "111")
    fake_ai(monkeypatch, f"Here you go.\nBOOKS: 999, {real['id']}")

    data = say(client).json()

    assert [b["title"] for b in data["books"]] == ["Dune"]


def test_reply_without_a_books_line_shows_no_books(client, monkeypatch):
    make_book(client, "Dune", "111")
    fake_ai(monkeypatch, "What kind of stories do you enjoy?")

    data = say(client).json()

    assert data["reply"] == "What kind of stories do you enjoy?"
    assert data["books"] == []


def test_earlier_messages_are_sent_to_the_ai(client, monkeypatch):
    make_book(client, "Dune", "111")
    seen = fake_ai(monkeypatch, "Sure.")

    client.post(
        "/api/ai/chat",
        json={
            "messages": [
                {"role": "user", "content": "I like space stories"},
                {"role": "assistant", "content": "Long or short?"},
                {"role": "user", "content": "Short please"},
            ]
        },
    )

    assert "I like space stories" in seen["prompt"]
    assert "Short please" in seen["prompt"]


def test_empty_library_does_not_call_the_ai(client, monkeypatch):
    def must_not_be_called(prompt, system=None):
        raise AssertionError("the AI should not be called for an empty library")

    monkeypatch.setattr("app.ai.client.ask", must_not_be_called)

    response = say(client)

    assert response.status_code == 200
    assert response.json()["books"] == []


def test_ai_failure_gives_503(client, monkeypatch):
    make_book(client, "Dune", "111")

    def broken(prompt, system=None):
        raise AIError("The AI service could not answer right now. Please try again.")

    monkeypatch.setattr("app.ai.client.ask", broken)

    assert say(client).status_code == 503


def test_requires_login(raw_client):
    assert say(raw_client).status_code == 401


def test_last_message_must_be_from_the_reader(client):
    response = client.post(
        "/api/ai/chat", json={"messages": [{"role": "assistant", "content": "Hello"}]}
    )

    assert response.status_code == 422


def test_needs_at_least_one_message(client):
    assert client.post("/api/ai/chat", json={"messages": []}).status_code == 422


def test_overlong_message_is_rejected(client):
    assert say(client, "x" * 1001).status_code == 422