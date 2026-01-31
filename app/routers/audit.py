"""
Router pour l'audit trail
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.schemas.audit import AuditLogResponse
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/user/{msisdn}/logs", response_model=list[AuditLogResponse])
async def get_user_audit_logs(
    msisdn: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupère les logs d'audit d'un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    - **limit**: Nombre maximum de logs à retourner (défaut: 100)
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    audit_service = AuditService(db)
    logs = audit_service.get_user_audit_logs(user.id, limit)
    
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/loan/{loan_id}/trail", response_model=list[AuditLogResponse])
async def get_loan_audit_trail(
    loan_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère le trail d'audit complet pour un crédit.
    
    - **loan_id**: ID du crédit
    """
    audit_service = AuditService(db)
    logs = audit_service.get_loan_audit_trail(loan_id)
    
    return [AuditLogResponse.model_validate(log) for log in logs]
