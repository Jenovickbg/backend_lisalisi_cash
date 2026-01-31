"""
Router pour la gestion des consentements (T&C)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.db.models import ConsentType
from app.schemas.consent import ConsentRequest, ConsentResponse, ConsentCheckResponse
from app.services.auth_service import AuthService
from app.services.consent_service import ConsentService

router = APIRouter(prefix="/consent", tags=["Consent"])


@router.post("/accept", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def accept_consent(
    consent_data: ConsentRequest,
    db: Session = Depends(get_db)
):
    """
    Accepte ou refuse un consentement (T&C).
    
    - **msisdn**: Numéro de téléphone
    - **consent_type**: Type de consentement (TERMS_AND_CONDITIONS ou SCORING_DATA_ACCESS)
    - **version**: Version du texte
    - **channel**: Canal (USSD ou APP)
    - **accepted**: True si accepté, False si refusé
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_msisdn(consent_data.msisdn)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )
        
        consent_service = ConsentService(db)
        consent = consent_service.accept_consent(
            user=user,
            consent_type=consent_data.consent_type,
            version=consent_data.version,
            channel=consent_data.channel,
            accepted=consent_data.accepted
        )
        
        return ConsentResponse.model_validate(consent)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/check/{msisdn}", response_model=ConsentCheckResponse)
async def check_consents(
    msisdn: str,
    db: Session = Depends(get_db)
):
    """
    Vérifie le statut des consentements d'un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    consent_service = ConsentService(db)
    result = consent_service.check_consents(user)
    
    return ConsentCheckResponse(**result)


@router.get("/text/{consent_type}")
async def get_consent_text(
    consent_type: ConsentType,
    db: Session = Depends(get_db)
):
    """
    Récupère le texte d'un consentement.
    
    - **consent_type**: Type de consentement
    """
    consent_service = ConsentService(db)
    text = consent_service.get_consent_text(consent_type)
    
    return {
        "consent_type": consent_type.value,
        "version": consent_service.TERMS_VERSION if consent_type == ConsentType.TERMS_AND_CONDITIONS else consent_service.SCORING_VERSION,
        "text": text
    }
