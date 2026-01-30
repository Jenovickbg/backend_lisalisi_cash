from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Endpoint de vérification de santé du service"""
    return {
        "status": "ok",
        "message": "Service opérationnel"
    }
