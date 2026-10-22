from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.join import JoinRequest, JoinResponse
from app.services import join_service
from app.services.rate_limiter import RateLimiter

# No login needed for anything in this router.
router = APIRouter(prefix="/api/public", tags=["Public"])

join_limiter = RateLimiter(max_requests=5, window_seconds=60 * 60)


def limit_join_requests(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    if not join_limiter.allow(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )


@router.post(
    "/join",
    response_model=JoinResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limit_join_requests)],
)
def join_library(data: JoinRequest, request: Request, db: Session = Depends(get_db)):
    member_id = join_service.request_to_join(db, data)

    # If a staff member is already signed in, leave their session as it is.
    if "user_id" not in request.session:
        # The visitor can browse and use the AI. Borrowing still needs staff approval.
        request.session["visitor"] = True
        # Remember which member this browser belongs to, so "My account" can show it.
        # (None when the email already existed: that person is NOT linked.)
        if member_id is not None:
            request.session["member_id"] = member_id

    return {
        "message": "Thank you! You can now browse books and use the AI. "
        "Staff will review your request before you can borrow."
    }