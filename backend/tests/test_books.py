BOOK = {
    "title": "Dune",
    "author": "Frank Herbert",
    "isbn": "9780441172719",
    "category": "Science Fiction",
    "total_copies": 2,
}


def make_book(client, **changes):
    """Helper: creates a book (Dune by default) and returns it as a dictionary."""
    response = client.post("/api/books", json={**BOOK, **changes})
    assert response.status_code == 201
    return response.json()


# ---------- Create ----------
def test_create_book(client):
    response = client.post("/api/books", json=BOOK)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"
    assert data["available_copies"] == 2  # a new book starts fully available


def test_duplicate_isbn_is_rejected(client):
    client.post("/api/books", json=BOOK)
    response = client.post("/api/books", json=BOOK)

    assert response.status_code == 409


def test_empty_title_is_rejected(client):
    response = client.post("/api/books", json={**BOOK, "title": ""})

    assert response.status_code == 422


# ---------- Read, search and filter ----------
def test_list_books(client):
    make_book(client)
    make_book(client, title="Atomic Habits", author="James Clear", isbn="9780735211292")

    response = client.get("/api/books")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_ignores_case(client):
    make_book(client)
    make_book(client, title="Atomic Habits", author="James Clear", isbn="9780735211292")

    response = client.get("/api/books", params={"search": "dUnE"})

    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Dune"


def test_filter_by_category(client):
    make_book(client)
    make_book(client, title="Atomic Habits", isbn="9780735211292", category="Self-help")

    response = client.get("/api/books", params={"category": "science fiction"})

    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Dune"


def test_limit_controls_page_size(client):
    for number in range(3):
        make_book(client, title=f"Book {number}", isbn=f"isbn-{number}")

    response = client.get("/api/books", params={"limit": 2})

    assert len(response.json()) == 2


def test_get_one_book(client):
    book = make_book(client)

    response = client.get(f"/api/books/{book['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Dune"


def test_get_missing_book_returns_404(client):
    response = client.get("/api/books/999")

    assert response.status_code == 404


# ---------- Update ----------
def test_update_changes_only_the_sent_fields(client):
    book = make_book(client)

    response = client.patch(f"/api/books/{book['id']}", json={"description": "A desert planet epic."})

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "A desert planet epic."
    assert data["title"] == "Dune"  # untouched


def test_changing_total_copies_updates_available_copies(client):
    book = make_book(client)  # 2 total, 2 available

    response = client.patch(f"/api/books/{book['id']}", json={"total_copies": 5})

    data = response.json()
    assert data["total_copies"] == 5
    assert data["available_copies"] == 5


def test_update_to_an_existing_isbn_is_rejected(client):
    make_book(client)
    other = make_book(client, title="Atomic Habits", isbn="9780735211292")

    response = client.patch(f"/api/books/{other['id']}", json={"isbn": BOOK["isbn"]})

    assert response.status_code == 409


def test_update_missing_book_returns_404(client):
    response = client.patch("/api/books/999", json={"title": "Nothing"})

    assert response.status_code == 404


# ---------- Delete ----------
def test_delete_book(client):
    book = make_book(client)

    response = client.delete(f"/api/books/{book['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/books/{book['id']}").status_code == 404


def test_delete_missing_book_returns_404(client):
    response = client.delete("/api/books/999")

    assert response.status_code == 404