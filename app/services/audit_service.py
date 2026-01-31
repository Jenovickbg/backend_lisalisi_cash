"""
Service d'audit trail pour traçabilité complète
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
from app.db.models import AuditLog, AuditEventType
from datetime import datetime


class AuditService:
    """Service de gestion de l'audit trail"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
        channel: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Enregistre un événement d'audit.
        
        Args:
            event_type: Type d'événement (register, set_pin, consent, etc.)
            user_id: ID de l'utilisateur (optionnel)
            event_data: Données de l'événement (sera sérialisé en JSON)
            channel: Canal (USSD ou APP)
            ip_address: Adresse IP
            
        Returns:
            AuditLog créé
        """
        # Convertir event_data en JSON string
        event_data_json = None
        if event_data:
            event_data_json = json.dumps(event_data, default=str)
        
        # Valider le type d'événement
        try:
            event_enum = AuditEventType(event_type)
        except ValueError:
            # Si le type n'existe pas dans l'enum, utiliser une valeur par défaut
            event_enum = AuditEventType.REGISTER
        
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_enum,
            event_data=event_data_json,
            channel=channel,
            ip_address=ip_address
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_user_audit_logs(self, user_id: int, limit: int = 100) -> list:
        """
        Récupère les logs d'audit d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum de logs à retourner
            
        Returns:
            Liste des AuditLog
        """
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
    
    def get_loan_audit_trail(self, loan_id: int) -> list:
        """
        Récupère le trail d'audit pour un crédit spécifique.
        
        Args:
            loan_id: ID du crédit
            
        Returns:
            Liste des événements liés au crédit
        """
        # Chercher les événements contenant le loan_id dans event_data
        all_logs = self.db.query(AuditLog).filter(
            AuditLog.event_type.in_([
                AuditEventType.LOAN_REQUEST,
                AuditEventType.LOAN_DECISION,
                AuditEventType.PAYOUT_SIMULATED,
                AuditEventType.REPAY
            ])
        ).all()
        
        # Filtrer ceux qui concernent ce crédit
        loan_logs = []
        for log in all_logs:
            if log.event_data:
                try:
                    data = json.loads(log.event_data)
                    if data.get("loan_id") == loan_id:
                        loan_logs.append(log)
                except:
                    pass
        
        return sorted(loan_logs, key=lambda x: x.created_at)
