from fastapi import FastAPI
from app.db.db import engine, Base
from app.routers import (
    health, ussd, auth, loan, consent, scoring, wallet, audit
)

# Création de l'application FastAPI
app = FastAPI(
    title="Fintech Backend API - Microcrédit Digital",
    description="""
    API backend pour système de microcrédit digital inclusif.
    
    ## Fonctionnalités
    
    * **Authentification** : Création de compte, gestion du PIN
    * **Consentements** : Gestion des termes et conditions (T&C)
    * **Scoring** : Calcul de score de crédit déterministe et explicable
    * **Microcrédits** : Demande, décision, remboursement
    * **Audit** : Trail complet pour traçabilité
    
    ## Architecture
    
    * Scoring basé sur données internes + externes (simulées)
    * Décisions explicables et traçables
    * Conforme aux exigences bancaires
    """,
    version="2.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Créer les tables de base de données au démarrage"""
    Base.metadata.create_all(bind=engine)


# Inclusion des routers
app.include_router(health.router)
app.include_router(ussd.router)
app.include_router(auth.router)
app.include_router(consent.router)
app.include_router(scoring.router)
app.include_router(loan.router)
app.include_router(wallet.router)
app.include_router(audit.router)


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Fintech Backend API - Microcrédit Digital",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/auth",
            "consent": "/consent",
            "scoring": "/scoring",
            "loans": "/loans",
            "wallet": "/wallet",
            "audit": "/audit",
            "ussd": "/ussd"
        }
    }
