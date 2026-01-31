"""
Router pour l'authentification et la gestion des utilisateurs
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.schemas.auth import (
    UserCreate, UserResponse, PinSetRequest, PinVerifyRequest, PinVerifyResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    channel: str = "APP",
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau compte utilisateur.
    
    - **msisdn**: Numéro de téléphone (MSISDN)
    - **full_name**: Nom complet (optionnel)
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(
            msisdn=user_data.msisdn,
            full_name=user_data.full_name,
            channel=channel
        )
        return UserResponse(
            id=user.id,
            msisdn=user.msisdn,
            full_name=user.full_name,
            has_pin=user.pin_hash is not None,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/set-pin", status_code=status.HTTP_200_OK)
async def set_pin(
    pin_data: PinSetRequest,
    channel: str = "APP",
    db: Session = Depends(get_db)
):
    """
    Définit ou met à jour le PIN d'un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    - **pin**: PIN à 4 chiffres
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_msisdn(pin_data.msisdn)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )
        
        auth_service.set_pin(user, pin_data.pin, channel)
        return {"message": "PIN défini avec succès"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-pin", response_model=PinVerifyResponse)
async def verify_pin(
    pin_data: PinVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Vérifie le PIN d'un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    - **pin**: PIN à vérifier
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(pin_data.msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    if not user.pin_hash:
        return PinVerifyResponse(
            valid=False,
            message="Aucun PIN défini"
        )
    
    is_valid = auth_service.verify_pin(user, pin_data.pin)
    
    if is_valid:
        # Mettre à jour le compteur d'utilisation
        auth_service.update_usage_count(user, "APP")
    
    return PinVerifyResponse(
        valid=is_valid,
        message="PIN correct" if is_valid else "PIN incorrect"
    )


@router.get("/user/{msisdn}", response_model=UserResponse)
async def get_user(
    msisdn: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les informations d'un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    return UserResponse(
        id=user.id,
        msisdn=user.msisdn,
        full_name=user.full_name,
        has_pin=user.pin_hash is not None,
        created_at=user.created_at
    )
