from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models import AuditEventType


class AuditLogResponse(BaseModel):
    """Schéma de réponse pour un log d'audit"""
    id: int
    user_id: Optional[int]
    event_type: AuditEventType
    event_data: Optional[str]
    channel: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
