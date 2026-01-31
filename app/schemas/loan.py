from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.db.models import LoanStatus


class LoanRequest(BaseModel):
    """Schéma pour demander un crédit"""
    msisdn: str = Field(..., description="Numéro de téléphone")
    pin: str = Field(..., min_length=4, max_length=4, description="PIN de l'utilisateur")
    amount: int = Field(..., gt=0, description="Montant demandé en FCFA")
    duration_days: int = Field(..., ge=7, le=90, description="Durée en jours (7, 14, 30, etc.)")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Valider le montant"""
        if v < 1000:
            raise ValueError("Le montant minimum est de 1000 FCFA")
        if v > 1000000:
            raise ValueError("Le montant maximum est de 1 000 000 FCFA")
        return v
    
    @field_validator('duration_days')
    @classmethod
    def validate_duration(cls, v):
        """Valider la durée"""
        if v not in [7, 14, 30, 60, 90]:
            raise ValueError("Durée invalide. Options: 7, 14, 30, 60, 90 jours")
        return v


class LoanResponse(BaseModel):
    """Schéma de réponse pour un crédit"""
    id: int
    user_id: int
    amount_requested: int
    amount_approved: Optional[int]
    amount_remaining: int
    interest_rate: float
    duration_days: int
    status: LoanStatus
    requested_at: datetime
    decided_at: Optional[datetime]
    due_date: Optional[datetime]
    repaid_at: Optional[datetime]
    score_at_request: Optional[float]
    decision_reason: Optional[str]
    
    class Config:
        from_attributes = True


class LoanDecisionResponse(BaseModel):
    """Réponse après une décision de crédit"""
    loan_id: int
    decision: str  # "APPROVED" ou "REJECTED"
    amount_approved: Optional[int]
    due_date: Optional[datetime]
    decision_reason: str
    score: Optional[float]
    score_explanation: Optional[str]


class LoanRepayRequest(BaseModel):
    """Schéma pour rembourser un crédit"""
    msisdn: str = Field(..., description="Numéro de téléphone")
    pin: str = Field(..., min_length=4, max_length=4, description="PIN de l'utilisateur")
    loan_id: int = Field(..., description="ID du crédit à rembourser")
    amount: int = Field(..., gt=0, description="Montant à rembourser en FCFA")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Valider le montant"""
        if v < 100:
            raise ValueError("Le montant minimum de remboursement est de 100 FCFA")
        return v


class LoanRepayResponse(BaseModel):
    """Réponse après un remboursement"""
    loan_id: int
    amount_paid: int
    amount_remaining: int
    is_fully_repaid: bool
    message: str


class LoanStatusResponse(BaseModel):
    """Statut d'un crédit"""
    loan_id: int
    status: str
    amount_requested: int
    amount_approved: Optional[int]
    amount_remaining: int
    due_date: Optional[datetime]
    days_remaining: Optional[int]
    is_overdue: bool
