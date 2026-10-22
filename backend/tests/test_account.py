from datetime import date, timedelta

from sqlalchemy import select

from app.models.book import Book
from app.models.borrow import BorrowRecord
from app.models.member import Member


# ---------- Helpers ----------
def join(client, name="Ravi Kumar", email="ravi@example.com"):
    response = client.post("/api/public/join", json={"name": name, "email": email})
    assert response.status_code == 201


def add_book(db, title="Dune"):
    book = Book(title=title, author="Frank Herbert", total_copies=2, available_copies=1)
    db.add(book)
    db.commit()
    return book


def add_loan(db, book, member, due_in_days=14):
    loan = BorrowRecord(
        book_id=book.id,
        member_id=member.id,
        issued_on=date.today(),
        due_on=date.today() + timedelta(days=due_in_days),
    )
    db.add(loan)
    db.commit()
    return loan


def the_joined_member(db):
    return db.scalar(select(Member).where(Member.email == "ravi@example.com"))


# ---------- Tests ----------
def test_joining_links_the_new_member(raw_client):
    join(raw_client)

    response = raw_client.get("/api/my/account")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Ravi Kumar",
        "email": "ravi@example.com",
        "status": "pending",
        "loans": [],
    }


def test_approved_member_sees_status_and_loans(raw_client, session_factory):
    join(raw_client)
    with session_factory() as db:
        member = the_joined_member(db)
        member.is_active = True  # what the librarian does on the Members page
        add_loan(db, add_book(db), member)

    data = raw_client.get("/api/my/account").json()

    assert data["status"] == "member"
    assert [loan["book_title"] for loan in data["loans"]] == ["Dune"]
    assert data["loans"][0]["returned_on"] is None
    assert data["loans"][0]["is_overdue"] is False


def test_an_overdue_loan_is_flagged(raw_client, session_factory):
    join(raw_client)
    with session_factory() as db:
        add_loan(db, add_book(db), the_joined_member(db), due_in_days=-3)

    assert raw_client.get("/api/my/account").json()["loans"][0]["is_overdue"] is True


def test_a_member_only_sees_their_own_loans(raw_client, session_factory):
    join(raw_client)
    with session_factory() as db:
        other = Member(name="Someone Else", email="other@example.com", is_active=True)
        db.add(other)
        db.commit()
        book = add_book(db)
        add_loan(db, book, other)  # a loan that belongs to somebody else

    assert raw_client.get("/api/my/account").json()["loans"] == []


def test_joining_with_an_existing_email_is_not_linked(raw_client, session_factory):
    with session_factory() as db:
        db.add(Member(name="Real Ravi", email="ravi@example.com", is_active=True))
        db.commit()

    join(raw_client)  # same email as the existing member

    assert raw_client.get("/api/my/account").status_code == 404


def test_account_needs_a_session(raw_client):
    assert raw_client.get("/api/my/account").status_code == 401


def test_deleted_member_gets_404(raw_client, session_factory):
    join(raw_client)
    with session_factory() as db:
        db.delete(the_joined_member(db))
        db.commit()

    assert raw_client.get("/api/my/account").status_code == 404