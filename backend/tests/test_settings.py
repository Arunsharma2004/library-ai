import pytest
from sqlalchemy import func, select

from app.config import DEFAULT_SECRET_KEY, check_production_settings
from app.models.user import User
from app.services.bootstrap import create_first_staff

GOOD_KEY = "k" * 40


# ---------- Production safety checks ----------
def test_development_allows_the_default_key():
    check_production_settings("development", DEFAULT_SECRET_KEY, False)  # no error


def test_production_refuses_the_default_key():
    with pytest.raises(RuntimeError):
        check_production_settings("production", DEFAULT_SECRET_KEY, True)


def test_production_refuses_a_short_key():
    with pytest.raises(RuntimeError):
        check_production_settings("production", "short", True)


def test_production_refuses_insecure_cookies():
    with pytest.raises(RuntimeError):
        check_production_settings("production", GOOD_KEY, False)


def test_production_accepts_good_settings():
    check_production_settings("production", GOOD_KEY, True)  # no error


# ---------- First staff account ----------
def test_first_staff_is_created(session_factory):
    with session_factory() as db:
        assert create_first_staff(db, " Librarian ", "a-strong-password") is True

        user = db.scalar(select(User))
        assert user.username == "librarian"
        assert user.password_hash != "a-strong-password"  # stored hashed, never as typed


def test_existing_staff_are_never_changed(session_factory):
    with session_factory() as db:
        create_first_staff(db, "librarian", "a-strong-password")

        assert create_first_staff(db, "someone-else", "another-password") is False
        assert db.scalar(select(func.count()).select_from(User)) == 1


def test_nothing_happens_without_settings(session_factory):
    with session_factory() as db:
        assert create_first_staff(db, None, None) is False
        assert create_first_staff(db, "librarian", "") is False
        assert db.scalar(select(func.count()).select_from(User)) == 0


def test_short_admin_password_is_refused(session_factory):
    with session_factory() as db:
        with pytest.raises(RuntimeError):
            create_first_staff(db, "librarian", "short")