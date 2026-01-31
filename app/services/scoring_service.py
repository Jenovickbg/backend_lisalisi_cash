"""
Service de scoring déterministe et explicable
Le scoring est basé sur des règles métier claires, sans ML en Phase 2.
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.db.models import User, ScoringData, Loan, LoanStatus
from app.services.external_data_simulator import ExternalDataSimulator
from datetime import datetime, timedelta


class ScoringService:
    """Service de calcul de score de crédit"""
    
    SCORE_VERSION = "1.0"
    MAX_SCORE = 1000
    MIN_SCORE = 0
    
    # Plafonds de crédit selon le score
    SCORE_THRESHOLDS = {
        800: 500000,  # Score >= 800: 500k FCFA
        700: 300000,  # Score >= 700: 300k FCFA
        600: 200000,  # Score >= 600: 200k FCFA
        500: 100000,  # Score >= 500: 100k FCFA
        400: 50000,   # Score >= 400: 50k FCFA
        0: 10000      # Score < 400: 10k FCFA (crédit d'amorçage)
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.external_simulator = ExternalDataSimulator()
    
    def calculate_score(self, user: User, force_recalculate: bool = False) -> Dict:
        """
        Calcule le score de crédit pour un utilisateur.
        
        Args:
            user: Utilisateur
            force_recalculate: Forcer le recalcul même si un score existe
            
        Returns:
            Dict avec score, explication, et données utilisées
        """
        # Vérifier si un score existe déjà
        scoring_data = self.db.query(ScoringData).filter(
            ScoringData.user_id == user.id
        ).first()
        
        if scoring_data and not force_recalculate:
            # Retourner le score existant
            return self._format_score_response(scoring_data)
        
        # Collecter les données internes
        internal_data = self._collect_internal_data(user)
        
        # Collecter les données externes (simulées)
        external_data = self.external_simulator.get_mobile_money_data(user.msisdn)
        
        # Calculer le score
        score_result = self._compute_score(internal_data, external_data)
        
        # Sauvegarder ou mettre à jour
        if scoring_data:
            self._update_scoring_data(scoring_data, internal_data, external_data, score_result)
        else:
            scoring_data = self._create_scoring_data(user.id, internal_data, external_data, score_result)
            self.db.add(scoring_data)
        
        self.db.commit()
        self.db.refresh(scoring_data)
        
        return self._format_score_response(scoring_data)
    
    def _collect_internal_data(self, user: User) -> Dict:
        """Collecte les données internes de l'utilisateur"""
        # Ancienneté du compte
        account_age_days = (datetime.now() - user.created_at).days
        
        # Fréquence d'utilisation
        ussd_count = user.ussd_usage_count
        app_count = user.app_usage_count
        total_usage = ussd_count + app_count
        
        # Historique de crédit
        loans = self.db.query(Loan).filter(Loan.user_id == user.id).all()
        total_loans = len(loans)
        repaid_loans = len([l for l in loans if l.status == LoanStatus.REPAID])
        overdue_loans = len([l for l in loans if l.status == LoanStatus.OVERDUE])
        
        # Vérifier s'il y a un crédit actif
        active_loan = self.db.query(Loan).filter(
            Loan.user_id == user.id,
            Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.PENDING])
        ).first()
        
        return {
            "account_age_days": account_age_days,
            "ussd_usage_count": ussd_count,
            "app_usage_count": app_count,
            "total_usage": total_usage,
            "total_loans_count": total_loans,
            "repaid_loans_count": repaid_loans,
            "overdue_loans_count": overdue_loans,
            "has_active_loan": active_loan is not None
        }
    
    def _compute_score(self, internal_data: Dict, external_data: Dict) -> Dict:
        """
        Calcule le score déterministe basé sur des règles métier.
        
        Score de base: 500 points
        Ajustements:
        - Ancienneté compte: +0 à +150 points
        - Utilisation: +0 à +100 points
        - Historique crédit: +0 à +150 points
        - Données externes: +0 à +100 points
        """
        score = 500  # Score de base
        factors = {}
        
        # 1. Ancienneté du compte (0-150 points)
        account_age_days = internal_data["account_age_days"]
        if account_age_days >= 365:
            age_score = 150
        elif account_age_days >= 180:
            age_score = 100
        elif account_age_days >= 90:
            age_score = 50
        elif account_age_days >= 30:
            age_score = 25
        else:
            age_score = 0
        score += age_score
        factors["account_age"] = {
            "value": account_age_days,
            "points": age_score,
            "max_points": 150
        }
        
        # 2. Fréquence d'utilisation (0-100 points)
        total_usage = internal_data["total_usage"]
        if total_usage >= 50:
            usage_score = 100
        elif total_usage >= 30:
            usage_score = 75
        elif total_usage >= 20:
            usage_score = 50
        elif total_usage >= 10:
            usage_score = 25
        else:
            usage_score = 0
        score += usage_score
        factors["usage_frequency"] = {
            "value": total_usage,
            "points": usage_score,
            "max_points": 100
        }
        
        # 3. Historique de crédit (0-150 points)
        total_loans = internal_data["total_loans_count"]
        repaid_loans = internal_data["repaid_loans_count"]
        overdue_loans = internal_data["overdue_loans_count"]
        
        if total_loans == 0:
            history_score = 0
        else:
            repayment_rate = repaid_loans / total_loans if total_loans > 0 else 0
            if repayment_rate >= 0.9 and overdue_loans == 0:
                history_score = 150
            elif repayment_rate >= 0.7 and overdue_loans == 0:
                history_score = 100
            elif repayment_rate >= 0.5:
                history_score = 50
            else:
                history_score = 0
            
            # Pénalité pour crédits en retard
            if overdue_loans > 0:
                history_score = max(0, history_score - (overdue_loans * 50))
        
        score += history_score
        factors["credit_history"] = {
            "total_loans": total_loans,
            "repaid_loans": repaid_loans,
            "overdue_loans": overdue_loans,
            "points": history_score,
            "max_points": 150
        }
        
        # 4. Données externes Mobile Money (0-100 points)
        mm_age = external_data.get("mm_account_age_months", 0)
        mm_volume = external_data.get("mm_monthly_volume_avg", 0)
        mm_transactions = external_data.get("mm_monthly_transactions_avg", 0)
        mm_regularity = external_data.get("mm_activity_regularity", 0.0)
        
        # Score basé sur l'ancienneté MM (0-40 points)
        if mm_age >= 24:
            mm_age_score = 40
        elif mm_age >= 12:
            mm_age_score = 30
        elif mm_age >= 6:
            mm_age_score = 20
        elif mm_age >= 3:
            mm_age_score = 10
        else:
            mm_age_score = 0
        
        # Score basé sur le volume et la régularité (0-60 points)
        volume_score = min(30, (mm_volume / 100000) * 10)  # Max 30 points
        regularity_score = mm_regularity * 30  # Max 30 points
        mm_activity_score = int(volume_score + regularity_score)
        
        external_score = mm_age_score + mm_activity_score
        score += external_score
        factors["external_data"] = {
            "mm_account_age_months": mm_age,
            "mm_monthly_volume_avg": mm_volume,
            "mm_activity_regularity": mm_regularity,
            "points": external_score,
            "max_points": 100
        }
        
        # Pénalité si crédit actif
        if internal_data["has_active_loan"]:
            score = max(0, score - 200)
            factors["active_loan_penalty"] = {
                "points": -200,
                "reason": "Un crédit actif réduit le score"
            }
        
        # Limiter le score entre MIN et MAX
        score = max(self.MIN_SCORE, min(self.MAX_SCORE, score))
        
        return {
            "score": score,
            "factors": factors,
            "explanation": self._generate_explanation(score, factors)
        }
    
    def _generate_explanation(self, score: float, factors: Dict) -> str:
        """Génère une explication textuelle du score"""
        explanations = []
        
        if factors.get("account_age", {}).get("points", 0) > 0:
            days = factors["account_age"]["value"]
            explanations.append(f"Compte actif depuis {days} jours")
        
        if factors.get("usage_frequency", {}).get("points", 0) > 0:
            usage = factors["usage_frequency"]["value"]
            explanations.append(f"Utilisation régulière ({usage} interactions)")
        
        if factors.get("credit_history", {}).get("points", 0) > 0:
            repaid = factors["credit_history"]["repaid_loans"]
            total = factors["credit_history"]["total_loans"]
            explanations.append(f"Historique positif ({repaid}/{total} crédits remboursés)")
        
        if factors.get("external_data", {}).get("points", 0) > 0:
            explanations.append("Données Mobile Money favorables")
        
        if factors.get("active_loan_penalty"):
            explanations.append("Un crédit actif limite le nouveau crédit")
        
        if not explanations:
            explanations.append("Score de base - Profil en construction")
        
        return ". ".join(explanations) + "."
    
    def _get_max_loan_amount(self, score: float) -> int:
        """Détermine le montant maximum de crédit selon le score"""
        for threshold, amount in sorted(self.SCORE_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return amount
        return self.SCORE_THRESHOLDS[0]
    
    def _format_score_response(self, scoring_data: ScoringData) -> Dict:
        """Formate la réponse de score"""
        max_loan = self._get_max_loan_amount(scoring_data.score or 0)
        
        return {
            "score": scoring_data.score,
            "score_version": scoring_data.score_version,
            "max_loan_amount": max_loan,
            "is_first_loan": scoring_data.total_loans_count == 0,
            "explanation": self._generate_explanation(
                scoring_data.score or 0,
                {
                    "account_age": {"value": scoring_data.account_age_days, "points": 0},
                    "usage_frequency": {"value": scoring_data.ussd_usage_count + scoring_data.app_usage_count, "points": 0},
                    "credit_history": {
                        "total_loans": scoring_data.total_loans_count,
                        "repaid_loans": scoring_data.repaid_loans_count,
                        "overdue_loans": scoring_data.overdue_loans_count,
                        "points": 0
                    },
                    "external_data": {
                        "mm_account_age_months": scoring_data.mm_account_age_months or 0,
                        "mm_monthly_volume_avg": scoring_data.mm_monthly_volume_avg or 0,
                        "mm_activity_regularity": scoring_data.mm_activity_regularity or 0.0,
                        "points": 0
                    }
                }
            )
        }
    
    def _create_scoring_data(self, user_id: int, internal_data: Dict, external_data: Dict, score_result: Dict) -> ScoringData:
        """Crée un nouvel enregistrement ScoringData"""
        return ScoringData(
            user_id=user_id,
            account_age_days=internal_data["account_age_days"],
            ussd_usage_count=internal_data["ussd_usage_count"],
            app_usage_count=internal_data["app_usage_count"],
            total_loans_count=internal_data["total_loans_count"],
            repaid_loans_count=internal_data["repaid_loans_count"],
            overdue_loans_count=internal_data["overdue_loans_count"],
            mm_account_age_months=external_data.get("mm_account_age_months"),
            mm_monthly_volume_avg=external_data.get("mm_monthly_volume_avg"),
            mm_monthly_transactions_avg=external_data.get("mm_monthly_transactions_avg"),
            mm_activity_regularity=external_data.get("mm_activity_regularity"),
            score=score_result["score"],
            score_version=self.SCORE_VERSION
        )
    
    def _update_scoring_data(self, scoring_data: ScoringData, internal_data: Dict, external_data: Dict, score_result: Dict):
        """Met à jour un enregistrement ScoringData existant"""
        scoring_data.account_age_days = internal_data["account_age_days"]
        scoring_data.ussd_usage_count = internal_data["ussd_usage_count"]
        scoring_data.app_usage_count = internal_data["app_usage_count"]
        scoring_data.total_loans_count = internal_data["total_loans_count"]
        scoring_data.repaid_loans_count = internal_data["repaid_loans_count"]
        scoring_data.overdue_loans_count = internal_data["overdue_loans_count"]
        scoring_data.mm_account_age_months = external_data.get("mm_account_age_months")
        scoring_data.mm_monthly_volume_avg = external_data.get("mm_monthly_volume_avg")
        scoring_data.mm_monthly_transactions_avg = external_data.get("mm_monthly_transactions_avg")
        scoring_data.mm_activity_regularity = external_data.get("mm_activity_regularity")
        scoring_data.score = score_result["score"]
        scoring_data.calculated_at = datetime.now()
