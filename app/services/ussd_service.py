"""
Service USSD pour gérer la navigation multi-niveaux et intégrer avec les services métier
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional, Tuple
from app.services.auth_service import AuthService
from app.services.consent_service import ConsentService
from app.services.loan_service import LoanService
from app.services.scoring_service import ScoringService
from app.db.models import User, ConsentType, Loan, LoanStatus


class USSDService:
    """Service de gestion USSD avec navigation multi-niveaux"""
    
    SYSTEM_NAME = "Lisalisi cash"
    
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(db)
        self.consent_service = ConsentService(db)
        self.loan_service = LoanService(db)
        self.scoring_service = ScoringService(db)
    
    def process_ussd_request(self, phone_number: str, text: str) -> Tuple[str, bool]:
        """
        Traite une requête USSD et retourne la réponse.
        
        Args:
            phone_number: Numéro de téléphone
            text: Texte de navigation USSD (ex: "1", "1*2", "1*2*3")
            
        Returns:
            Tuple (response, is_end)
            - response: Texte à afficher
            - is_end: True si la session se termine (END), False si continue (CON)
        """
        # Nettoyer et parser le texte
        text = text.strip() if text else ""
        parts = text.split("*") if text else []
        
        # Menu principal (première interaction)
        if not text or text == "":
            return self._get_main_menu(), False
        
        # Navigation par niveau
        level = len(parts)
        first_choice = parts[0] if parts else ""
        
        # Niveau 1 : Menu principal
        if level == 1:
            return self._handle_level_1(first_choice, phone_number)
        
        # Niveau 2 : Sous-menus
        elif level == 2:
            return self._handle_level_2(first_choice, parts[1], phone_number, parts)
        
        # Niveau 3+ : Actions spécifiques
        elif level >= 3:
            return self._handle_level_3_plus(first_choice, parts, phone_number)
        
        return self._error_response("Option invalide"), True
    
    def _get_main_menu(self) -> str:
        """Menu principal"""
        menu = f"CON Bienvenue sur {self.SYSTEM_NAME}\n"
        menu += "1. Creer un compte\n"
        menu += "2. Definir PIN\n"
        menu += "3. Accepter T&C\n"
        menu += "4. Consulter offre credit\n"
        menu += "5. Demander credit\n"
        menu += "6. Rembourser credit\n"
        menu += "7. Historique credits\n"
        menu += "0. Quitter"
        return menu
    
    def _handle_level_1(self, choice: str, phone_number: str) -> Tuple[str, bool]:
        """Gère les choix du niveau 1"""
        if choice == "1":
            return self._handle_create_account(phone_number)
        elif choice == "2":
            return self._handle_set_pin_menu(phone_number)
        elif choice == "3":
            return self._handle_consent_menu(phone_number)
        elif choice == "4":
            return self._handle_check_offer(phone_number)
        elif choice == "5":
            return self._handle_loan_request_menu(phone_number)
        elif choice == "6":
            return self._handle_repay_menu(phone_number)
        elif choice == "7":
            return self._handle_history(phone_number)
        elif choice == "0":
            return "END Merci d'avoir utilise " + self.SYSTEM_NAME, True
        else:
            return self._error_response("Option invalide"), True
    
    def _handle_level_2(self, main_choice: str, sub_choice: str, phone_number: str, parts: list) -> Tuple[str, bool]:
        """Gère les choix du niveau 2"""
        if main_choice == "2":  # Définir PIN
            return self._handle_set_pin_input(phone_number, sub_choice)
        elif main_choice == "3":  # Consentements
            return self._handle_consent_choice(phone_number, sub_choice)
        elif main_choice == "5":  # Demander crédit
            return self._handle_loan_amount(phone_number, sub_choice, parts)
        elif main_choice == "6":  # Rembourser
            return self._handle_repay_loan_choice(phone_number, sub_choice, parts)
        else:
            return self._error_response("Option invalide"), True
    
    def _handle_level_3_plus(self, main_choice: str, parts: list, phone_number: str) -> Tuple[str, bool]:
        """Gère les niveaux 3 et plus"""
        if main_choice == "2":  # PIN
            if len(parts) >= 3:
                return self._handle_set_pin_confirm(phone_number, parts[1], parts[2])
        elif main_choice == "5":  # Demander crédit
            if len(parts) >= 3:
                return self._handle_loan_duration(phone_number, parts[1], parts[2], parts)
            elif len(parts) >= 4:
                return self._handle_loan_pin(phone_number, parts[1], parts[2], parts[3], parts)
        elif main_choice == "6":  # Rembourser
            if len(parts) >= 3:
                return self._handle_repay_amount(phone_number, parts[1], parts[2], parts)
            elif len(parts) >= 4:
                return self._handle_repay_pin(phone_number, parts[1], parts[2], parts[3], parts)
        
        return self._error_response("Option invalide"), True
    
    # ========== GESTION COMPTE ==========
    
    def _handle_create_account(self, phone_number: str) -> Tuple[str, bool]:
        """Créer un compte"""
        try:
            # Vérifier si le compte existe déjà
            user = self.auth_service.get_user_by_msisdn(phone_number)
            if user:
                return f"END Compte existe deja pour {phone_number}\nUtilisez option 2 pour definir PIN", True
            
            # Créer le compte
            user = self.auth_service.create_user(
                msisdn=phone_number,
                full_name=None,
                channel="USSD"
            )
            
            return f"END Compte cree avec succes!\nNumero: {phone_number}\nDefinissez votre PIN (option 2)", True
        except ValueError as e:
            return f"END Erreur: {str(e)}", True
        except Exception as e:
            return f"END Erreur lors de la creation du compte", True
    
    # ========== GESTION PIN ==========
    
    def _handle_set_pin_menu(self, phone_number: str) -> Tuple[str, bool]:
        """Menu pour définir PIN"""
        user = self.auth_service.get_user_by_msisdn(phone_number)
        if not user:
            return "END Compte introuvable. Creer un compte d'abord (option 1)", True
        
        if user.pin_hash:
            return "CON PIN deja defini. Voulez-vous le changer?\n1. Oui\n2. Non", False
        
        return "CON Entrez votre PIN (4 chiffres):", False
    
    def _handle_set_pin_input(self, phone_number: str, pin: str) -> Tuple[str, bool]:
        """Saisie du PIN"""
        if not pin.isdigit() or len(pin) != 4:
            return "END PIN invalide. Doit contenir 4 chiffres", True
        
        return "CON Confirmez votre PIN:", False
    
    def _handle_set_pin_confirm(self, phone_number: str, pin: str, confirm_pin: str) -> Tuple[str, bool]:
        """Confirmation du PIN"""
        if pin != confirm_pin:
            return "END Les PIN ne correspondent pas. Reessayez", True
        
        try:
            user = self.auth_service.get_user_by_msisdn(phone_number)
            if not user:
                return "END Compte introuvable", True
            
            self.auth_service.set_pin(user, pin, channel="USSD")
            return "END PIN defini avec succes!", True
        except Exception as e:
            return f"END Erreur: {str(e)}", True
    
    # ========== GESTION CONSENTEMENTS ==========
    
    def _handle_consent_menu(self, phone_number: str) -> Tuple[str, bool]:
        """Menu des consentements"""
        user = self.auth_service.get_user_by_msisdn(phone_number)
        if not user:
            return "END Compte introuvable. Creer un compte d'abord", True
        
        consents = self.consent_service.check_consents(user)
        
        menu = "CON Termes et Conditions\n"
        if not consents["has_terms_consent"]:
            menu += "1. Accepter T&C\n"
        else:
            menu += "1. T&C deja acceptes\n"
        
        if not consents["has_scoring_consent"]:
            menu += "2. Accepter Scoring\n"
        else:
            menu += "2. Scoring deja accepte\n"
        
        menu += "0. Retour"
        return menu, False
    
    def _handle_consent_choice(self, phone_number: str, choice: str) -> Tuple[str, bool]:
        """Gère le choix de consentement"""
        user = self.auth_service.get_user_by_msisdn(phone_number)
        if not user:
            return "END Compte introuvable", True
        
        if choice == "1":
            consent_type = ConsentType.TERMS_AND_CONDITIONS
        elif choice == "2":
            consent_type = ConsentType.SCORING_DATA_ACCESS
        elif choice == "0":
            return self._get_main_menu(), False
        else:
            return self._error_response("Option invalide"), True
        
        try:
            consent = self.consent_service.accept_consent(
                user=user,
                consent_type=consent_type,
                version="1.0",
                channel="USSD",
                accepted=True
            )
            return f"END Consentement accepte avec succes!", True
        except Exception as e:
            return f"END Erreur: {str(e)}", True
    
    # ========== GESTION OFFRE ==========
    
    def _handle_check_offer(self, phone_number: str) -> Tuple[str, bool]:
        """Consulter l'offre de crédit"""
        try:
            user = self.auth_service.get_user_by_msisdn(phone_number)
            if not user:
                return "END Compte introuvable. Creer un compte d'abord", True
            
            score_result = self.scoring_service.calculate_score(user)
            
            response = f"END Offre de credit:\n"
            response += f"Score: {score_result['score']:.0f}/1000\n"
            response += f"Montant max: {score_result['max_loan_amount']:,} FCFA\n"
            response += f"{score_result['explanation']}"
            
            return response, True
        except Exception as e:
            return f"END Erreur: {str(e)}", True
    
    # ========== GESTION DEMANDE CRÉDIT ==========
    
    def _handle_loan_request_menu(self, phone_number: str) -> Tuple[str, bool]:
        """Menu demande de crédit"""
        user = self.auth_service.get_user_by_msisdn(phone_number)
        if not user:
            return "END Compte introuvable", True
        
        if not user.pin_hash:
            return "END PIN non defini. Definissez votre PIN d'abord", True
        
        # Vérifier les consentements
        consents = self.consent_service.check_consents(user)
        if not consents["can_request_loan"]:
            return "END Acceptez les T&C d'abord (option 3)", True
        
        # Vérifier crédit actif (sera vérifié dans loan_service)
        
        # Récupérer l'offre
        score_result = self.scoring_service.calculate_score(user)
        
        menu = f"CON Demande de credit\n"
        menu += f"Montant max: {score_result['max_loan_amount']:,} FCFA\n"
        menu += "Entrez le montant (FCFA):"
        return menu, False
    
    def _handle_loan_amount(self, phone_number: str, amount_str: str, parts: list) -> Tuple[str, bool]:
        """Saisie du montant"""
        try:
            amount = int(amount_str)
            if amount < 1000:
                return "END Montant minimum: 1000 FCFA", True
            if amount > 1000000:
                return "END Montant maximum: 1000000 FCFA", True
            
            # Stocker temporairement (dans une vraie app, utiliser session/cache)
            # Pour l'instant, on continue avec le montant dans les parts
            menu = "CON Duree du credit:\n"
            menu += "1. 7 jours\n"
            menu += "2. 14 jours\n"
            menu += "3. 30 jours\n"
            menu += "4. 60 jours\n"
            menu += "5. 90 jours"
            return menu, False
        except ValueError:
            return "END Montant invalide. Entrez un nombre", True
    
    def _handle_loan_duration(self, phone_number: str, amount_str: str, duration_choice: str, parts: list) -> Tuple[str, bool]:
        """Choix de la durée"""
        duration_map = {
            "1": 7,
            "2": 14,
            "3": 30,
            "4": 60,
            "5": 90
        }
        
        duration = duration_map.get(duration_choice)
        if not duration:
            return self._error_response("Duree invalide"), True
        
        return "CON Entrez votre PIN pour confirmer:", False
    
    def _handle_loan_pin(self, phone_number: str, amount_str: str, duration_choice: str, pin: str, parts: list) -> Tuple[str, bool]:
        """Confirmation PIN et demande de crédit"""
        try:
            user = self.auth_service.get_user_by_msisdn(phone_number)
            if not user:
                return "END Compte introuvable", True
            
            if not self.auth_service.verify_pin(user, pin):
                return "END PIN incorrect", True
            
            duration_map = {"1": 7, "2": 14, "3": 30, "4": 60, "5": 90}
            amount = int(amount_str)
            duration = duration_map.get(duration_choice, 30)
            
            # Demander le crédit
            loan = self.loan_service.request_loan(
                user=user,
                amount=amount,
                duration_days=duration,
                channel="USSD"
            )
            
            if loan.status.value == "APPROVED":
                response = f"END Credit approuve!\n"
                response += f"Montant: {loan.amount_approved:,} FCFA\n"
                response += f"Echeance: {loan.due_date.strftime('%d/%m/%Y') if loan.due_date else 'N/A'}\n"
                response += f"ID Credit: {loan.id}"
            else:
                response = f"END Credit refuse\n"
                response += f"Raison: {loan.decision_reason or 'Non specifie'}"
            
            return response, True
        except ValueError as e:
            return f"END Erreur: {str(e)}", True
        except Exception as e:
            return f"END Erreur lors de la demande: {str(e)}", True
    
    # ========== GESTION REMBOURSEMENT ==========
    
    def _handle_repay_menu(self, phone_number: str) -> Tuple[str, bool]:
        """Menu remboursement"""
        user = self.auth_service.get_user_by_msisdn(phone_number)
        if not user:
            return "END Compte introuvable", True
        
        loans = self.loan_service.get_user_loans(user)
        active_loans = [l for l in loans if l.status.value in ["ACTIVE", "OVERDUE"]]
        
        if not active_loans:
            return "END Aucun credit actif a rembourser", True
        
        menu = "CON Credits actifs:\n"
        for i, loan in enumerate(active_loans[:5], 1):  # Max 5 crédits
            menu += f"{i}. Credit #{loan.id}: {loan.amount_remaining:,} FCFA\n"
        menu += "0. Retour"
        return menu, False
    
    def _handle_repay_loan_choice(self, phone_number: str, choice: str, parts: list) -> Tuple[str, bool]:
        """Choix du crédit à rembourser"""
        if choice == "0":
            return self._get_main_menu(), False
        
        try:
            loan_index = int(choice) - 1
            user = self.auth_service.get_user_by_msisdn(phone_number)
            loans = self.loan_service.get_user_loans(user)
            active_loans = [l for l in loans if l.status.value in ["ACTIVE", "OVERDUE"]]
            
            if loan_index < 0 or loan_index >= len(active_loans):
                return self._error_response("Credit invalide"), True
            
            loan = active_loans[loan_index]
            menu = f"CON Rembourser Credit #{loan.id}\n"
            menu += f"Montant restant: {loan.amount_remaining:,} FCFA\n"
            menu += "Entrez le montant a rembourser:"
            return menu, False
        except ValueError:
            return self._error_response("Option invalide"), True
    
    def _handle_repay_amount(self, phone_number: str, loan_index_str: str, amount_str: str, parts: list) -> Tuple[str, bool]:
        """Saisie du montant de remboursement"""
        try:
            amount = int(amount_str)
            if amount < 100:
                return "END Montant minimum: 100 FCFA", True
            
            return "CON Entrez votre PIN pour confirmer:", False
        except ValueError:
            return "END Montant invalide", True
    
    def _handle_repay_pin(self, phone_number: str, loan_index_str: str, amount_str: str, pin: str, parts: list) -> Tuple[str, bool]:
        """Confirmation PIN et remboursement"""
        try:
            user = self.auth_service.get_user_by_msisdn(phone_number)
            if not user:
                return "END Compte introuvable", True
            
            if not self.auth_service.verify_pin(user, pin):
                return "END PIN incorrect", True
            
            loan_index = int(loan_index_str) - 1
            loans = self.loan_service.get_user_loans(user)
            active_loans = [l for l in loans if l.status.value in ["ACTIVE", "OVERDUE"]]
            
            if loan_index < 0 or loan_index >= len(active_loans):
                return "END Credit invalide", True
            
            loan = active_loans[loan_index]
            amount = int(amount_str)
            
            result = self.loan_service.repay_loan(
                user=user,
                loan_id=loan.id,
                amount=amount,
                channel="USSD"
            )
            
            if result["is_fully_repaid"]:
                response = f"END Credit rembourse completement!\n"
                response += f"Montant paye: {result['amount_paid']:,} FCFA"
            else:
                response = f"END Remboursement effectue\n"
                response += f"Montant paye: {result['amount_paid']:,} FCFA\n"
                response += f"Reste: {result['amount_remaining']:,} FCFA"
            
            return response, True
        except ValueError as e:
            return f"END Erreur: {str(e)}", True
        except Exception as e:
            return f"END Erreur: {str(e)}", True
    
    # ========== GESTION HISTORIQUE ==========
    
    def _handle_history(self, phone_number: str) -> Tuple[str, bool]:
        """Consulter l'historique"""
        try:
            user = self.auth_service.get_user_by_msisdn(phone_number)
            if not user:
                return "END Compte introuvable", True
            
            loans = self.loan_service.get_user_loans(user)
            
            if not loans:
                return "END Aucun credit dans l'historique", True
            
            response = "END Historique credits:\n"
            for loan in loans[:5]:  # Max 5 crédits
                status_emoji = "✅" if loan.status.value == "REPAID" else "⏳" if loan.status.value == "ACTIVE" else "❌"
                response += f"{status_emoji} #{loan.id}: {loan.amount_requested:,} FCFA\n"
                response += f"   Statut: {loan.status.value}\n"
            
            if len(loans) > 5:
                response += f"\n... et {len(loans) - 5} autres"
            
            return response, True
        except Exception as e:
            return f"END Erreur: {str(e)}", True
    
    # ========== HELPERS ==========
    
    def _error_response(self, message: str) -> str:
        """Format de réponse d'erreur"""
        return f"END {message}\nTapez * pour retourner au menu"
    
    def _success_response(self, message: str) -> str:
        """Format de réponse de succès"""
        return f"END {message}"
