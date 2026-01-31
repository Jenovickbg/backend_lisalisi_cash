"""
Service de gestion des microcrédits
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.models import User, Loan, LoanStatus
from app.services.scoring_service import ScoringService
from app.services.consent_service import ConsentService
from app.services.audit_service import AuditService
from app.services.external_data_simulator import ExternalDataSimulator


class LoanService:
    """Service de gestion des crédits"""
    
    # Taux d'intérêt par défaut (en pourcentage)
    DEFAULT_INTEREST_RATE = 5.0  # 5% pour les premiers crédits
    STANDARD_INTEREST_RATE = 3.0  # 3% pour les crédits suivants
    
    def __init__(self, db: Session):
        self.db = db
        self.scoring_service = ScoringService(db)
        self.consent_service = ConsentService(db)
        self.audit_service = AuditService(db)
        self.external_simulator = ExternalDataSimulator()
    
    def request_loan(
        self,
        user: User,
        amount: int,
        duration_days: int,
        channel: str = "APP"
    ) -> Loan:
        """
        Traite une demande de crédit.
        
        Args:
            user: Utilisateur
            amount: Montant demandé
            duration_days: Durée en jours
            channel: Canal (USSD ou APP)
            
        Returns:
            Loan créé avec décision
        """
        # Vérifier les consentements
        consents = self.consent_service.check_consents(user)
        if not consents["can_request_loan"]:
            raise ValueError("Les consentements requis ne sont pas acceptés")
        
        # Vérifier qu'il n'y a pas de crédit actif
        active_loan = self.db.query(Loan).filter(
            Loan.user_id == user.id,
            Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.PENDING])
        ).first()
        
        if active_loan:
            raise ValueError("Un crédit est déjà actif. Veuillez le rembourser d'abord.")
        
        # Calculer le score
        score_result = self.scoring_service.calculate_score(user, force_recalculate=True)
        score = score_result["score"]
        max_loan_amount = score_result["max_loan_amount"]
        
        # Vérifier le montant demandé
        if amount > max_loan_amount:
            raise ValueError(
                f"Montant demandé ({amount}) dépasse le plafond autorisé ({max_loan_amount} FCFA)"
            )
        
        # Déterminer le taux d'intérêt
        is_first_loan = score_result["is_first_loan"]
        interest_rate = self.DEFAULT_INTEREST_RATE if is_first_loan else self.STANDARD_INTEREST_RATE
        
        # Calculer le montant approuvé (avec intérêts)
        interest_amount = int(amount * (interest_rate / 100))
        amount_approved = amount + interest_amount
        
        # Prendre une décision
        # Pour le MVP, on approuve si le score >= 400
        decision = LoanStatus.APPROVED if score >= 400 else LoanStatus.REJECTED
        decision_reason = self._generate_decision_reason(score, amount, max_loan_amount, decision)
        
        # Calculer la date d'échéance
        due_date = datetime.now() + timedelta(days=duration_days) if decision == LoanStatus.APPROVED else None
        
        # Créer le crédit
        loan = Loan(
            user_id=user.id,
            amount_requested=amount,
            amount_approved=amount_approved if decision == LoanStatus.APPROVED else None,
            amount_remaining=amount_approved if decision == LoanStatus.APPROVED else 0,
            interest_rate=interest_rate,
            duration_days=duration_days,
            status=LoanStatus.ACTIVE if decision == LoanStatus.APPROVED else LoanStatus.REJECTED,
            decided_at=datetime.now(),
            due_date=due_date,
            score_at_request=score,
            score_explanation=score_result["explanation"],
            decision_reason=decision_reason
        )
        
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        
        # Audit - Demande
        self.audit_service.log_event(
            event_type="loan_request",
            user_id=user.id,
            event_data={
                "loan_id": loan.id,
                "amount_requested": amount,
                "duration_days": duration_days,
                "score": score,
                "max_loan_amount": max_loan_amount
            },
            channel=channel
        )
        
        # Si approuvé, simuler le décaissement
        if decision == LoanStatus.APPROVED:
            payout_result = self.external_simulator.simulate_payout(user.msisdn, amount)
            
            # Audit - Décision
            self.audit_service.log_event(
                event_type="loan_decision",
                user_id=user.id,
                event_data={
                    "loan_id": loan.id,
                    "decision": "APPROVED",
                    "amount_approved": amount_approved,
                    "due_date": due_date.isoformat() if due_date else None,
                    "score": score,
                    "reason": decision_reason
                },
                channel=channel
            )
            
            # Audit - Décaissement simulé
            self.audit_service.log_event(
                event_type="payout_simulated",
                user_id=user.id,
                event_data={
                    "loan_id": loan.id,
                    "amount": amount,
                    "transaction_id": payout_result["transaction_id"],
                    "status": payout_result["status"]
                },
                channel=channel
            )
        else:
            # Audit - Rejet
            self.audit_service.log_event(
                event_type="loan_decision",
                user_id=user.id,
                event_data={
                    "loan_id": loan.id,
                    "decision": "REJECTED",
                    "score": score,
                    "reason": decision_reason
                },
                channel=channel
            )
        
        return loan
    
    def repay_loan(
        self,
        user: User,
        loan_id: int,
        amount: int,
        channel: str = "APP"
    ) -> dict:
        """
        Traite un remboursement de crédit.
        
        Args:
            user: Utilisateur
            loan_id: ID du crédit
            amount: Montant à rembourser
            channel: Canal (USSD ou APP)
            
        Returns:
            Dict avec les détails du remboursement
        """
        # Récupérer le crédit
        loan = self.db.query(Loan).filter(
            Loan.id == loan_id,
            Loan.user_id == user.id
        ).first()
        
        if not loan:
            raise ValueError("Crédit introuvable")
        
        if loan.status not in [LoanStatus.ACTIVE, LoanStatus.OVERDUE]:
            raise ValueError(f"Ce crédit ne peut pas être remboursé (statut: {loan.status.value})")
        
        if amount > loan.amount_remaining:
            raise ValueError(
                f"Le montant ({amount}) dépasse le montant restant ({loan.amount_remaining} FCFA)"
            )
        
        # Mettre à jour le montant restant
        loan.amount_remaining -= amount
        
        # Vérifier si le crédit est entièrement remboursé
        is_fully_repaid = loan.amount_remaining == 0
        if is_fully_repaid:
            loan.status = LoanStatus.REPAID
            loan.repaid_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(loan)
        
        # Audit
        self.audit_service.log_event(
            event_type="repay",
            user_id=user.id,
            event_data={
                "loan_id": loan.id,
                "amount_paid": amount,
                "amount_remaining": loan.amount_remaining,
                "is_fully_repaid": is_fully_repaid
            },
            channel=channel
        )
        
        return {
            "loan_id": loan.id,
            "amount_paid": amount,
            "amount_remaining": loan.amount_remaining,
            "is_fully_repaid": is_fully_repaid,
            "message": "Crédit entièrement remboursé" if is_fully_repaid else f"Montant restant: {loan.amount_remaining} FCFA"
        }
    
    def get_loan_status(self, user: User, loan_id: int) -> dict:
        """
        Récupère le statut d'un crédit.
        
        Args:
            user: Utilisateur
            loan_id: ID du crédit
            
        Returns:
            Dict avec le statut du crédit
        """
        loan = self.db.query(Loan).filter(
            Loan.id == loan_id,
            Loan.user_id == user.id
        ).first()
        
        if not loan:
            raise ValueError("Crédit introuvable")
        
        # Calculer les jours restants
        days_remaining = None
        is_overdue = False
        if loan.due_date:
            delta = loan.due_date - datetime.now()
            days_remaining = delta.days
            is_overdue = days_remaining < 0
        
        return {
            "loan_id": loan.id,
            "status": loan.status.value,
            "amount_requested": loan.amount_requested,
            "amount_approved": loan.amount_approved,
            "amount_remaining": loan.amount_remaining,
            "due_date": loan.due_date.isoformat() if loan.due_date else None,
            "days_remaining": days_remaining,
            "is_overdue": is_overdue
        }
    
    def get_user_loans(self, user: User) -> list:
        """
        Récupère tous les crédits d'un utilisateur.
        
        Args:
            user: Utilisateur
            
        Returns:
            Liste des crédits
        """
        return self.db.query(Loan).filter(
            Loan.user_id == user.id
        ).order_by(Loan.requested_at.desc()).all()
    
    def _generate_decision_reason(
        self,
        score: float,
        amount: int,
        max_amount: int,
        decision: LoanStatus
    ) -> str:
        """Génère une explication de la décision"""
        if decision == LoanStatus.APPROVED:
            return f"Crédit approuvé. Score: {score:.0f}, Montant autorisé: {max_amount} FCFA"
        else:
            if score < 400:
                return f"Score insuffisant ({score:.0f}/1000). Score minimum requis: 400"
            elif amount > max_amount:
                return f"Montant demandé ({amount}) dépasse le plafond ({max_amount} FCFA)"
            else:
                return "Crédit refusé pour raisons de scoring"
