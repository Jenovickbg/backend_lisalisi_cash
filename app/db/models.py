from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.db import Base


class LoanStatus(str, enum.Enum):
    """Statut d'un crédit"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    REPAID = "REPAID"
    OVERDUE = "OVERDUE"


class ConsentType(str, enum.Enum):
    """Type de consentement"""
    TERMS_AND_CONDITIONS = "TERMS_AND_CONDITIONS"
    SCORING_DATA_ACCESS = "SCORING_DATA_ACCESS"


class AuditEventType(str, enum.Enum):
    """Types d'événements d'audit"""
    REGISTER = "register"
    SET_PIN = "set_pin"
    CONSENT = "consent"
    LOAN_REQUEST = "loan_request"
    LOAN_DECISION = "loan_decision"
    PAYOUT_SIMULATED = "payout_simulated"
    REPAY = "repay"


class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    msisdn = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    pin_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    ussd_usage_count = Column(Integer, default=0, nullable=False)
    app_usage_count = Column(Integer, default=0, nullable=False)
    
    # Relations
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Wallet(Base):
    """Modèle portefeuille"""
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Integer, default=0, nullable=False)
    savings_balance = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relation 1-1 avec User
    user = relationship("User", back_populates="wallet")


class Loan(Base):
    """Modèle de crédit"""
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_requested = Column(Integer, nullable=False)
    amount_approved = Column(Integer, nullable=True)
    amount_remaining = Column(Integer, nullable=False)
    interest_rate = Column(Float, default=0.0, nullable=False)
    duration_days = Column(Integer, nullable=False)
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.PENDING, nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    repaid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Scoring snapshot
    score_at_request = Column(Float, nullable=True)
    score_explanation = Column(Text, nullable=True)
    decision_reason = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="loans")


class Consent(Base):
    """Modèle de consentement (T&C)"""
    __tablename__ = "consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_type = Column(SQLEnum(ConsentType), nullable=False)
    version = Column(String, nullable=False)
    accepted = Column(Boolean, default=False, nullable=False)
    channel = Column(String, nullable=False)  # "USSD" ou "APP"
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="consents")


class AuditLog(Base):
    """Modèle d'audit trail"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable pour les événements système
    event_type = Column(SQLEnum(AuditEventType), nullable=False)
    event_data = Column(Text, nullable=True)  # JSON string pour les détails
    channel = Column(String, nullable=True)  # "USSD" ou "APP"
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="audit_logs")


class ScoringData(Base):
    """Modèle pour stocker les données de scoring (cache)"""
    __tablename__ = "scoring_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Données internes
    account_age_days = Column(Integer, default=0, nullable=False)
    ussd_usage_count = Column(Integer, default=0, nullable=False)
    app_usage_count = Column(Integer, default=0, nullable=False)
    total_loans_count = Column(Integer, default=0, nullable=False)
    repaid_loans_count = Column(Integer, default=0, nullable=False)
    overdue_loans_count = Column(Integer, default=0, nullable=False)
    
    # Données externes simulées (Mobile Money)
    mm_account_age_months = Column(Integer, nullable=True)
    mm_monthly_volume_avg = Column(Integer, nullable=True)
    mm_monthly_transactions_avg = Column(Integer, nullable=True)
    mm_activity_regularity = Column(Float, nullable=True)  # 0.0 à 1.0
    
    # Score calculé
    score = Column(Float, nullable=True)
    score_version = Column(String, default="1.0", nullable=False)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    user = relationship("User")
