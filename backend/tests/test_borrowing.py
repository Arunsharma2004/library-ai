from datetime import date, timedelta

from app.models.borrow import BorrowRecord


# ---------- Helpers ----------
def make_book(client, title="Dune", isbn="9780441172719", copies=1):
    response = client.post(
        "/api/books",
        json={"title": title, "author": "Frank Herbert", "isbn": isbn, "total_copies": copies},
    )
    assert response.status_code == 201
    return response.json()


def make_member(client, name="Asha Rao", email="asha@example.com"):
    response = client.post("/api/members", json={"name": name, "email": email})
    assert response.status_code == 201
    return response.json()


def issue(client, book, member):
    return client.post("/api/borrows/issue", json={"book_id": book["id"], "member_id": member["id"]})


def available_copies(client, book):
    return client.get(f"/api/books/{book['id']}").json()["available_copies"]


# ---------- Issuing ----------
def test_issue_reduces_available_copies(client):
    book = make_book(client, copies=2)
    member = make_member(client)

    response = issue(client, book, member)

    assert response.status_code == 201
    assert available_copies(client, book) == 1


def test_due_date_is_14_days_away(client):
    book = make_book(client)
    member = make_member(client)

    loan = issue(client, book, member).json()

    assert loan["due_on"] == (date.today() + timedelta(days=14)).isoformat()
    assert loan["returned_on"] is None


def test_cannot_issue_when_no_copies_are_left(client):
    book = make_book(client, copies=1)
    asha = make_member(client)
    ravi = make_member(client, name="Ravi Kumar", email="ravi@example.com")
    issue(client, book, asha)

    response = issue(client, book, ravi)

    assert response.status_code == 409
    assert available_copies(client, book) == 0


def test_cannot_issue_to_an_inactive_member(client):
    book = make_book(client)
    member = make_member(client)
    client.patch(f"/api/members/{member['id']}", json={"is_active": False})

    response = issue(client, book, member)

    assert response.status_code == 409
    assert available_copies(client, book) == 1  # nothing changed


def test_member_cannot_borrow_the_same_book_twice(client):
    book = make_book(client, copies=2)
    member = make_member(client)
    issue(client, book, member)

    response = issue(client, book, member)

    assert response.status_code == 409


def test_issue_unknown_book_or_member_returns_404(client):
    book = make_book(client)
    member = make_member(client)

    assert issue(client, {"id": 999}, member).status_code == 404
    assert issue(client, book, {"id": 999}).status_code == 404


# ---------- Returning ----------
def test_return_restores_the_copy(client):
    book = make_book(client)
    member = make_member(client)
    loan = issue(client, book, member).json()

    response = client.post(f"/api/borrows/{loan['id']}/return")

    assert response.status_code == 200
    assert response.json()["returned_on"] is not None
    assert available_copies(client, book) == 1


def test_cannot_return_twice(client):
    book = make_book(client)
    member = make_member(client)
    loan = issue(client, book, member).json()
    client.post(f"/api/borrows/{loan['id']}/return")

    response = client.post(f"/api/borrows/{loan['id']}/return")

    assert response.status_code == 409
    assert available_copies(client, book) == 1  # not increased a second time


def test_return_unknown_record_returns_404(client):
    response = client.post("/api/borrows/999/return")

    assert response.status_code == 404


# ---------- Listing ----------
def test_list_loans_by_status(client):
    book = make_book(client, copies=2)
    asha = make_member(client)
    ravi = make_member(client, name="Ravi Kumar", email="ravi@example.com")
    first = issue(client, book, asha).json()
    issue(client, book, ravi)
    client.post(f"/api/borrows/{first['id']}/return")

    all_loans = client.get("/api/borrows").json()
    active = client.get("/api/borrows", params={"status": "active"}).json()
    returned = client.get("/api/borrows", params={"status": "returned"}).json()

    assert len(all_loans) == 2
    assert len(active) == 1
    assert len(returned) == 1
    assert returned[0]["member_name"] == "Asha Rao"


def test_overdue_logic():
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)

    late = BorrowRecord(due_on=yesterday, returned_on=None)
    on_time = BorrowRecord(due_on=tomorrow, returned_on=None)
    returned_late = BorrowRecord(due_on=yesterday, returned_on=date.today())

    assert late.is_overdue is True
    assert on_time.is_overdue is False
    assert returned_late.is_overdue is False  # a returned book is never overdue


# ---------- Rules that connect books, members and loans ----------
def test_cannot_delete_a_book_with_borrowing_history(client):
    book = make_book(client)
    member = make_member(client)
    loan = issue(client, book, member).json()
    client.post(f"/api/borrows/{loan['id']}/return")  # even after it was returned

    response = client.delete(f"/api/books/{book['id']}")

    assert response.status_code == 409


def test_cannot_delete_a_member_with_borrowing_history(client):
    book = make_book(client)
    member = make_member(client)
    issue(client, book, member)

    response = client.delete(f"/api/members/{member['id']}")

    assert response.status_code == 409


def test_total_copies_cannot_drop_below_the_borrowed_number(client):
    book = make_book(client, copies=3)
    asha = make_member(client)
    ravi = make_member(client, name="Ravi Kumar", email="ravi@example.com")
    issue(client, book, asha)
    issue(client, book, ravi)  # 2 copies are out

    too_low = client.patch(f"/api/books/{book['id']}", json={"total_copies": 1})
    allowed = client.patch(f"/api/books/{book['id']}", json={"total_copies": 2})

    assert too_low.status_code == 409
    assert allowed.status_code == 200
    assert allowed.json()["available_copies"] == 0  # both copies are still borrowed


def test_available_only_filter_hides_fully_borrowed_books(client):
    borrowed = make_book(client, title="Dune", isbn="111", copies=1)
    make_book(client, title="Emma", isbn="222", copies=1)
    member = make_member(client)
    issue(client, borrowed, member)

    results = client.get("/api/books", params={"available_only": True}).json()

    assert [book["title"] for book in results] == ["Emma"]