from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.rate_limiter import RateLimiter

# AI limits for visitors. Staff are never limited.
visitor_ai_limiter = RateLimiter(max_requests=25, window_seconds=60 * 60)       # per visitor, per hour
site_ai_limiter = RateLimiter(max_requests=200, window_seconds=60 * 60 * 24)    # all visitors, per day


def find_staff_user(request: Request, db: Session) -> User | None:
    """The staff user stored in the session cookie, or None."""
    user_id = request.session.get("user_id")
    return db.get(User, user_id) if user_id else None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """STAFF ONLY. 401 if nobody is signed in, 403 if the person is only a visitor."""
    user = find_staff_user(request, db)
    if user is None:
        if request.session.get("visitor"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="This is only for library staff"
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in")
    return user


def require_staff_or_visitor(request: Request, db: Session = Depends(get_db)) -> str:
    """For routes that visitors may use too. Returns "staff" or "visitor"."""
    if find_staff_user(request, db) is not None:
        return "staff"
    if request.session.get("visitor"):
        return "visitor"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please sign in")


def check_ai_limits(request: Request, role: str = Depends(require_staff_or_visitor)) -> None:
    """Protects the free AI quota: limits visitors per hour, and everyone together per day."""
    if role == "staff":
        return
    ip = request.client.host if request.client else "unknown"
    if not visitor_ai_limiter.allow(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You have used your AI requests for this hour. Please try again later.",
        )
    if not site_ai_limiter.allow("site"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="The AI has reached its limit for today. Please try again tomorrow.",
        )