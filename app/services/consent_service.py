"""
Service de gestion des consentements (T&C)
"""
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import User, Consent, ConsentType
from app.services.audit_service import AuditService


class ConsentService:
    """Service de gestion des consentements"""
    
    TERMS_VERSION = "1.0"
    SCORING_VERSION = "1.0"
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def accept_consent(
        self,
        user: User,
        consent_type: ConsentType,
        version: str,
        channel: str,
        accepted: bool = True
    ) -> Consent:
        """
        Enregistre un consentement utilisateur.
        
        Args:
            user: Utilisateur
            consent_type: Type de consentement
            version: Version du texte
            channel: Canal (USSD ou APP)
            accepted: True si accepté
            
        Returns:
            Consent créé ou mis à jour
        """
        # Vérifier si un consentement existe déjà
        existing = self.db.query(Consent).filter(
            Consent.user_id == user.id,
            Consent.consent_type == consent_type
        ).first()
        
        if existing:
            # Mettre à jour
            existing.version = version
            existing.accepted = accepted
            existing.channel = channel
            if accepted:
                existing.accepted_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            consent = existing
        else:
            # Créer nouveau
            consent = Consent(
                user_id=user.id,
                consent_type=consent_type,
                version=version,
                accepted=accepted,
                channel=channel,
                accepted_at=datetime.now() if accepted else None
            )
            self.db.add(consent)
            self.db.commit()
            self.db.refresh(consent)
        
        # Audit
        self.audit_service.log_event(
            user_id=user.id,
            event_type="consent",
            event_data={
                "consent_type": consent_type.value,
                "version": version,
                "accepted": accepted,
                "channel": channel
            },
            channel=channel
        )
        
        return consent
    
    def check_consents(self, user: User) -> dict:
        """
        Vérifie les consentements d'un utilisateur.
        
        Returns:
            Dict avec le statut des consentements
        """
        terms_consent = self.db.query(Consent).filter(
            Consent.user_id == user.id,
            Consent.consent_type == ConsentType.TERMS_AND_CONDITIONS,
            Consent.accepted == True
        ).first()
        
        scoring_consent = self.db.query(Consent).filter(
            Consent.user_id == user.id,
            Consent.consent_type == ConsentType.SCORING_DATA_ACCESS,
            Consent.accepted == True
        ).first()
        
        has_terms = terms_consent is not None
        has_scoring = scoring_consent is not None
        can_request_loan = has_terms and has_scoring
        
        message = "Consentements complets" if can_request_loan else "Consentements manquants"
        
        return {
            "has_terms_consent": has_terms,
            "has_scoring_consent": has_scoring,
            "can_request_loan": can_request_loan,
            "message": message
        }
    
    def get_consent_text(self, consent_type: ConsentType) -> str:
        """
        Retourne le texte du consentement.
        
        En production, cela pourrait être stocké en DB ou dans un fichier.
        """
        if consent_type == ConsentType.TERMS_AND_CONDITIONS:
            return """TERMES ET CONDITIONS - VERSION 1.0

En utilisant ce service de microcrédit, vous acceptez que :
1. Les données de votre compte Mobile Money soient utilisées pour le scoring de crédit
2. Les décisions de crédit sont basées sur des algorithmes automatisés
3. Vous êtes responsable du remboursement de vos crédits
4. Des frais d'intérêt peuvent s'appliquer

En acceptant, vous donnez votre consentement pour l'accès à vos données agrégées Mobile Money."""
        
        elif consent_type == ConsentType.SCORING_DATA_ACCESS:
            return """ACCÈS AUX DONNÉES DE SCORING - VERSION 1.0

Pour évaluer votre éligibilité au crédit, nous utilisons :
- L'ancienneté de votre compte
- Votre historique d'utilisation
- Vos données Mobile Money agrégées (volume, fréquence, régularité)

Ces données sont utilisées uniquement pour le scoring et ne sont pas partagées avec des tiers."""
        
        return ""
