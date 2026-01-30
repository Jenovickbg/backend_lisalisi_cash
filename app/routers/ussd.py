from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class USSDRequest(BaseModel):
    """Modèle de requête USSD compatible Africa's Talking"""
    sessionId: str
    phoneNumber: str
    text: str = ""


@router.post("/ussd")
async def ussd_handler(request: USSDRequest):
    """
    Endpoint USSD compatible Africa's Talking
    Format de réponse: CON ... ou END ...
    """
    text = request.text.strip()
    
    # Menu principal (première interaction)
    if text == "":
        response = "CON Bienvenue au service Fintech\n"
        response += "1. Consulter le solde\n"
        response += "2. Autres options\n"
        return {"response": response}
    
    # Option 1: Afficher solde fictif
    elif text == "1":
        response = "END Votre solde: 1000 FCFA\n"
        response += "Merci d'avoir utilisé notre service."
        return {"response": response}
    
    # Option invalide
    else:
        response = "END Option invalide. Veuillez réessayer."
        return {"response": response}
