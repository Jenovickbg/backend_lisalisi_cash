"""
Router pour le scoring et les offres de crédit
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.schemas.scoring import ScoringDataResponse
from app.services.auth_service import AuthService
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/scoring", tags=["Scoring"])


@router.get("/{msisdn}/offer", response_model=ScoringDataResponse)
async def get_credit_offer(
    msisdn: str,
    db: Session = Depends(get_db)
):
    """
    Récupère l'offre de crédit (score et plafond) pour un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    
    Retourne le score, le montant maximum autorisé, et une explication,
    sans exposer les données brutes de scoring.
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    scoring_service = ScoringService(db)
    score_result = scoring_service.calculate_score(user)
    
    return ScoringDataResponse(**score_result)
