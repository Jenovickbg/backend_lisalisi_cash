"""
Router pour la gestion du portefeuille
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.schemas.wallet import WalletResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/{msisdn}", response_model=WalletResponse)
async def get_wallet(
    msisdn: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les informations du portefeuille d'un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    if not user.wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portefeuille introuvable"
        )
    
    return WalletResponse.model_validate(user.wallet)
