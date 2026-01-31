"""
Router pour la gestion des microcrédits
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.schemas.loan import (
    LoanRequest, LoanResponse, LoanDecisionResponse,
    LoanRepayRequest, LoanRepayResponse, LoanStatusResponse
)
from app.services.auth_service import AuthService
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans"])


def get_user_with_pin_verification(
    msisdn: str,
    pin: str,
    db: Session
):
    """Helper pour vérifier l'utilisateur et son PIN"""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    if not user.pin_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN non défini. Veuillez définir un PIN d'abord."
        )
    
    if not auth_service.verify_pin(user, pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="PIN incorrect"
        )
    
    return user


@router.post("/request", response_model=LoanDecisionResponse, status_code=status.HTTP_201_CREATED)
async def request_loan(
    loan_request: LoanRequest,
    channel: str = "APP",
    db: Session = Depends(get_db)
):
    """
    Demande un microcrédit.
    
    - **msisdn**: Numéro de téléphone
    - **pin**: PIN de l'utilisateur
    - **amount**: Montant demandé en FCFA
    - **duration_days**: Durée en jours (7, 14, 30, 60, 90)
    """
    try:
        # Vérifier l'utilisateur et le PIN
        user = get_user_with_pin_verification(
            loan_request.msisdn,
            loan_request.pin,
            db
        )
        
        # Traiter la demande
        loan_service = LoanService(db)
        loan = loan_service.request_loan(
            user=user,
            amount=loan_request.amount,
            duration_days=loan_request.duration_days,
            channel=channel
        )
        
        # Formater la réponse
        return LoanDecisionResponse(
            loan_id=loan.id,
            decision=loan.status.value,
            amount_approved=loan.amount_approved,
            due_date=loan.due_date,
            decision_reason=loan.decision_reason or "Décision prise",
            score=loan.score_at_request,
            score_explanation=loan.score_explanation
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/repay", response_model=LoanRepayResponse)
async def repay_loan(
    repay_request: LoanRepayRequest,
    channel: str = "APP",
    db: Session = Depends(get_db)
):
    """
    Rembourse un crédit.
    
    - **msisdn**: Numéro de téléphone
    - **pin**: PIN de l'utilisateur
    - **loan_id**: ID du crédit à rembourser
    - **amount**: Montant à rembourser en FCFA
    """
    try:
        # Vérifier l'utilisateur et le PIN
        user = get_user_with_pin_verification(
            repay_request.msisdn,
            repay_request.pin,
            db
        )
        
        # Traiter le remboursement
        loan_service = LoanService(db)
        result = loan_service.repay_loan(
            user=user,
            loan_id=repay_request.loan_id,
            amount=repay_request.amount,
            channel=channel
        )
        
        return LoanRepayResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{loan_id}/status", response_model=LoanStatusResponse)
async def get_loan_status(
    loan_id: int,
    msisdn: str,
    db: Session = Depends(get_db)
):
    """
    Récupère le statut d'un crédit.
    
    - **loan_id**: ID du crédit
    - **msisdn**: Numéro de téléphone
    """
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_msisdn(msisdn)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur introuvable"
            )
        
        loan_service = LoanService(db)
        status_data = loan_service.get_loan_status(user, loan_id)
        
        return LoanStatusResponse(**status_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/user/{msisdn}/history", response_model=list[LoanResponse])
async def get_loan_history(
    msisdn: str,
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des crédits d'un utilisateur.
    
    - **msisdn**: Numéro de téléphone
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_msisdn(msisdn)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable"
        )
    
    loan_service = LoanService(db)
    loans = loan_service.get_user_loans(user)
    
    return [LoanResponse.model_validate(loan) for loan in loans]
