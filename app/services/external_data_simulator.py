"""
Simulateur de données externes (Mobile Money)
Ce module simule les données d'un fournisseur Mobile Money.
En production, ce module sera remplacé par un connecteur réel.
"""
import random
from typing import Dict, Optional
from datetime import datetime, timedelta


class ExternalDataSimulator:
    """Simulateur de données externes Mobile Money"""
    
    @staticmethod
    def get_mobile_money_data(msisdn: str) -> Dict:
        """
        Simule les données Mobile Money pour un MSISDN donné.
        
        En production, cette méthode appellera un vrai API de fournisseur télécom.
        
        Args:
            msisdn: Numéro de téléphone
            
        Returns:
            Dict contenant:
                - mm_account_age_months: Ancienneté du compte (mois)
                - mm_monthly_volume_avg: Volume mensuel moyen (FCFA)
                - mm_monthly_transactions_avg: Nombre de transactions mensuelles
                - mm_activity_regularity: Régularité d'activité (0.0 à 1.0)
        """
        # Utiliser le MSISDN comme seed pour avoir des données cohérentes
        # pour le même utilisateur
        random.seed(hash(msisdn) % 1000000)
        
        # Simuler des données réalistes
        account_age_months = random.randint(1, 60)  # 1 à 60 mois
        
        # Volume mensuel moyen (plus élevé si compte ancien)
        base_volume = random.randint(50000, 500000)
        volume_multiplier = 1 + (account_age_months / 60) * 0.5
        monthly_volume_avg = int(base_volume * volume_multiplier)
        
        # Nombre de transactions mensuelles
        monthly_transactions_avg = random.randint(5, 50)
        
        # Régularité d'activité (0.0 à 1.0)
        # Plus le compte est ancien, plus la régularité est élevée
        base_regularity = random.uniform(0.3, 0.9)
        regularity_boost = min(account_age_months / 60 * 0.2, 0.2)
        activity_regularity = min(base_regularity + regularity_boost, 1.0)
        
        return {
            "mm_account_age_months": account_age_months,
            "mm_monthly_volume_avg": monthly_volume_avg,
            "mm_monthly_transactions_avg": monthly_transactions_avg,
            "mm_activity_regularity": round(activity_regularity, 2)
        }
    
    @staticmethod
    def simulate_payout(msisdn: str, amount: int) -> Dict:
        """
        Simule un décaissement Mobile Money.
        
        Args:
            msisdn: Numéro de téléphone
            amount: Montant à décaisser
            
        Returns:
            Dict avec les détails de la transaction simulée
        """
        # Simuler un délai de traitement
        transaction_id = f"MM_{msisdn}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "transaction_id": transaction_id,
            "msisdn": msisdn,
            "amount": amount,
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat(),
            "note": "Transaction simulée - Pas de décaissement réel"
        }
