from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.client import AIError
from app.database import get_db
from app.dependencies import check_ai_limits, get_current_user
from app.schemas.assistant import ChatRequest, ChatResponse
from app.schemas.description import DescribeRequest, DescribeResponse
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services import assistant_service, description_service, recommendation_service

router = APIRouter(prefix="/api/ai", tags=["AI"])


# Staff and visitors (visitors are rate limited).
@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    dependencies=[Depends(check_ai_limits)],
)
def recommend_books(data: RecommendationRequest, db: Session = Depends(get_db)):
    try:
        picks = recommendation_service.recommend(db, data)
    except AIError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    return {"recommendations": [{"book": book, "reason": reason} for book, reason in picks]}


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(check_ai_limits)])
def chat(data: ChatRequest, db: Session = Depends(get_db)):
    try:
        reply, books = assistant_service.chat(db, data.messages)
    except AIError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    return {"reply": reply, "books": books}


# Staff only: this one is part of managing the catalog.
@router.post(
    "/describe", response_model=DescribeResponse, dependencies=[Depends(get_current_user)]
)
def describe_book(data: DescribeRequest):
    try:
        return {"description": description_service.describe(data)}
    except AIError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))