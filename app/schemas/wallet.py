from pydantic import BaseModel
from datetime import datetime


class WalletResponse(BaseModel):
    """Schéma de réponse pour un portefeuille"""
    id: int
    user_id: int
    balance: int
    savings_balance: int
    created_at: datetime
    
    class Config:
        from_attributes = True
