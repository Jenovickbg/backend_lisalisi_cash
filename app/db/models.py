from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base


class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    msisdn = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    pin_hash = Column(String, nullable=True)
    
    # Relation 1-1 avec Wallet
    wallet = relationship("Wallet", back_populates="user", uselist=False)


class Wallet(Base):
    """Modèle portefeuille"""
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Integer, default=0, nullable=False)
    savings_balance = Column(Integer, default=0, nullable=False)
    
    # Relation 1-1 avec User
    user = relationship("User", back_populates="wallet")
