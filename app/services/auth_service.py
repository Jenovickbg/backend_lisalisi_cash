"""
Service d'authentification et gestion des utilisateurs
"""
from sqlalchemy.orm import Session
from app.db.models import User, Wallet
from app.core.security import hash_password, verify_password
from app.services.audit_service import AuditService
from datetime import datetime


class AuthService:
    """Service d'authentification"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def create_user(self, msisdn: str, full_name: str = None, channel: str = "APP") -> User:
        """
        Crée un nouvel utilisateur avec son wallet.
        
        Args:
            msisdn: Numéro de téléphone
            full_name: Nom complet (optionnel)
            channel: Canal de création (USSD ou APP)
            
        Returns:
            User créé
        """
        # Vérifier si l'utilisateur existe déjà
        existing_user = self.db.query(User).filter(User.msisdn == msisdn).first()
        if existing_user:
            raise ValueError("Un utilisateur avec ce numéro existe déjà")
        
        # Créer l'utilisateur
        user = User(
            msisdn=msisdn,
            full_name=full_name
        )
        self.db.add(user)
        self.db.flush()  # Pour obtenir l'ID
        
        # Créer le wallet associé
        wallet = Wallet(
            user_id=user.id,
            balance=0,
            savings_balance=0
        )
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(user)
        
        # Audit
        self.audit_service.log_event(
            event_type="register",
            user_id=user.id,
            event_data={
                "msisdn": msisdn,
                "full_name": full_name,
                "channel": channel
            },
            channel=channel
        )
        
        return user
    
    def set_pin(self, user: User, pin: str, channel: str = "APP") -> User:
        """
        Définit ou met à jour le PIN d'un utilisateur.
        
        Args:
            user: Utilisateur
            pin: PIN à 4 chiffres
            channel: Canal (USSD ou APP)
            
        Returns:
            User mis à jour
        """
        # Hasher le PIN
        pin_hash = hash_password(pin)
        user.pin_hash = pin_hash
        self.db.commit()
        self.db.refresh(user)
        
        # Audit (sans logger le PIN)
        self.audit_service.log_event(
            event_type="set_pin",
            user_id=user.id,
            event_data={
                "pin_set": True,
                "channel": channel
            },
            channel=channel
        )
        
        return user
    
    def verify_pin(self, user: User, pin: str) -> bool:
        """
        Vérifie le PIN d'un utilisateur.
        
        Args:
            user: Utilisateur
            pin: PIN à vérifier
            
        Returns:
            True si le PIN est correct
        """
        if not user.pin_hash:
            return False
        
        return verify_password(pin, user.pin_hash)
    
    def get_user_by_msisdn(self, msisdn: str) -> User:
        """
        Récupère un utilisateur par son MSISDN.
        
        Args:
            msisdn: Numéro de téléphone
            
        Returns:
            User ou None
        """
        return self.db.query(User).filter(User.msisdn == msisdn).first()
    
    def update_usage_count(self, user: User, channel: str):
        """
        Met à jour le compteur d'utilisation.
        
        Args:
            user: Utilisateur
            channel: Canal (USSD ou APP)
        """
        if channel.upper() == "USSD":
            user.ussd_usage_count += 1
        elif channel.upper() == "APP":
            user.app_usage_count += 1
        
        user.last_login = datetime.now()
        self.db.commit()
