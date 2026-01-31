from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.services.ussd_service import USSDService

router = APIRouter()


class USSDRequest(BaseModel):
    """Modèle de requête USSD compatible Africa's Talking"""
    sessionId: str
    phoneNumber: str
    text: str = ""


@router.post("/ussd")
async def ussd_handler(
    request: USSDRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint USSD compatible Africa's Talking - Lisalisi cash
    
    Navigation multi-niveaux avec toutes les fonctionnalités :
    - Création de compte
    - Définir PIN
    - Accepter T&C
    - Consulter offre de crédit
    - Demander crédit
    - Rembourser crédit
    - Consulter historique
    
    Format de réponse: CON ... ou END ...
    """
    ussd_service = USSDService(db)
    
    # Traiter la requête USSD
    response_text, is_end = ussd_service.process_ussd_request(
        phone_number=request.phoneNumber,
        text=request.text
    )
    
    # Mettre à jour le compteur d'utilisation USSD si utilisateur existe
    try:
        from app.services.auth_service import AuthService
        auth_service = AuthService(db)
        user = auth_service.get_user_by_msisdn(request.phoneNumber)
        if user:
            auth_service.update_usage_count(user, "USSD")
    except:
        pass  # Ignorer les erreurs de comptage
    
    return {"response": response_text}
