from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.db.models import ConsentType


class ConsentRequest(BaseModel):
    """Schéma pour accepter un consentement"""
    msisdn: str = Field(..., description="Numéro de téléphone")
    consent_type: ConsentType = Field(..., description="Type de consentement")
    version: str = Field(..., description="Version du texte de consentement")
    channel: str = Field(..., description="Canal: USSD ou APP")
    accepted: bool = Field(True, description="True si accepté, False si refusé")
    
    @field_validator('channel')
    @classmethod
    def validate_channel(cls, v):
        """Valider le canal"""
        if v.upper() not in ["USSD", "APP"]:
            raise ValueError("Le canal doit être USSD ou APP")
        return v.upper()


class ConsentResponse(BaseModel):
    """Schéma de réponse pour un consentement"""
    id: int
    user_id: int
    consent_type: ConsentType
    version: str
    accepted: bool
    channel: str
    accepted_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConsentCheckResponse(BaseModel):
    """Vérification du statut de consentement"""
    has_terms_consent: bool
    has_scoring_consent: bool
    can_request_loan: bool
    message: str
