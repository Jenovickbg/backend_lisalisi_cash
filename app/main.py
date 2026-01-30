from fastapi import FastAPI
from app.db.db import engine, Base
from app.routers import health, ussd

# Création de l'application FastAPI
app = FastAPI(
    title="Fintech Backend API",
    description="API backend pour application fintech (USSD + mobile)",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Créer les tables de base de données au démarrage"""
    Base.metadata.create_all(bind=engine)


# Inclusion des routers
app.include_router(health.router, tags=["Health"])
app.include_router(ussd.router, tags=["USSD"])


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Fintech Backend API",
        "docs": "/docs",
        "health": "/health"
    }
