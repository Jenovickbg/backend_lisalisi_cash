from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schéma pour la création d'un utilisateur"""
    msisdn: str = Field(..., description="Numéro de téléphone (MSISDN)")
    full_name: Optional[str] = Field(None, description="Nom complet de l'utilisateur")
    
    @field_validator('msisdn')
    @classmethod
    def validate_msisdn(cls, v):
        """Valider le format MSISDN"""
        if not v or len(v) < 9:
            raise ValueError("MSISDN invalide")
        return v.strip()


class UserResponse(BaseModel):
    """Schéma de réponse pour un utilisateur"""
    id: int
    msisdn: str
    full_name: Optional[str]
    has_pin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PinSetRequest(BaseModel):
    """Schéma pour définir un PIN"""
    msisdn: str = Field(..., description="Numéro de téléphone")
    pin: str = Field(..., min_length=4, max_length=4, description="PIN à 4 chiffres")
    
    @field_validator('pin')
    @classmethod
    def validate_pin(cls, v):
        """Valider que le PIN contient uniquement des chiffres"""
        if not v.isdigit():
            raise ValueError("Le PIN doit contenir uniquement des chiffres")
        return v


class PinVerifyRequest(BaseModel):
    """Schéma pour vérifier un PIN"""
    msisdn: str = Field(..., description="Numéro de téléphone")
    pin: str = Field(..., min_length=4, max_length=4, description="PIN à 4 chiffres")
    
    @field_validator('pin')
    @classmethod
    def validate_pin(cls, v):
        """Valider que le PIN contient uniquement des chiffres"""
        if not v.isdigit():
            raise ValueError("Le PIN doit contenir uniquement des chiffres")
        return v


class PinVerifyResponse(BaseModel):
    """Réponse de vérification de PIN"""
    valid: bool
    message: str
