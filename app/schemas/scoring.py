from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ScoringDataResponse(BaseModel):
    """Données de scoring (sans score brut)"""
    score: Optional[float] = Field(None, description="Score calculé (0-1000)")
    score_version: str = Field(..., description="Version de l'algorithme de scoring")
    max_loan_amount: int = Field(..., description="Montant maximum de crédit autorisé")
    is_first_loan: bool = Field(..., description="True si c'est le premier crédit")
    explanation: str = Field(..., description="Explication du score")
    
    class Config:
        from_attributes = True


class ScoringExplanationResponse(BaseModel):
    """Explication détaillée du scoring"""
    score: float
    score_version: str
    factors: dict = Field(..., description="Facteurs de scoring détaillés")
    max_loan_amount: int
    explanation: str
