from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.client import AIError
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services import recommendation_service

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/recommendations", response_model=RecommendationResponse)
def recommend_books(data: RecommendationRequest, db: Session = Depends(get_db)):
    try:
        picks = recommendation_service.recommend(db, data)
    except AIError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))
    return {"recommendations": [{"book": book, "reason": reason} for book, reason in picks]}