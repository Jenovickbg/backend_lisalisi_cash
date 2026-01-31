# Phase 2 - Backend Microcrédit Digital

## 🎯 Vue d'ensemble

Backend FastAPI complet pour un système de microcrédit digital inclusif, accessible via USSD et application mobile.

## ✨ Fonctionnalités implémentées

### 1. Authentification
- ✅ Création de compte (MSISDN unique)
- ✅ Définition et vérification de PIN (4 chiffres, hashé avec bcrypt)
- ✅ Gestion des compteurs d'utilisation (USSD/APP)

### 2. Consentements (T&C)
- ✅ Acceptation des termes et conditions
- ✅ Consentement pour accès aux données de scoring
- ✅ Vérification des consentements avant demande de crédit
- ✅ Trail d'audit pour chaque consentement

### 3. Scoring déterministe
- ✅ Calcul de score basé sur :
  - Données internes (ancienneté, utilisation, historique crédit)
  - Données externes simulées (Mobile Money)
- ✅ Score explicable et traçable
- ✅ Plafonds de crédit selon le score
- ✅ Pas de Machine Learning (Phase 2)

### 4. Microcrédits
- ✅ Demande de crédit avec validation
- ✅ Décision automatique (APPROVED/REJECTED)
- ✅ Un seul crédit actif par utilisateur
- ✅ Crédit d'amorçage pour premiers crédits
- ✅ Remboursement partiel ou total
- ✅ Suivi du statut et échéances

### 5. Audit Trail
- ✅ Enregistrement de tous les événements importants
- ✅ Trail complet par utilisateur
- ✅ Trail par crédit
- ✅ Données immuables et traçables

## 📁 Structure du code

```
app/
├── main.py                 # Application FastAPI principale
├── core/
│   ├── config.py          # Configuration
│   └── security.py        # Hashage PIN
├── db/
│   ├── db.py              # Configuration SQLAlchemy
│   └── models.py          # Modèles DB (User, Loan, Consent, etc.)
├── schemas/
│   ├── auth.py            # Schémas authentification
│   ├── loan.py            # Schémas crédit
│   ├── consent.py         # Schémas consentement
│   ├── scoring.py         # Schémas scoring
│   ├── wallet.py          # Schémas portefeuille
│   └── audit.py           # Schémas audit
├── services/
│   ├── auth_service.py    # Service authentification
│   ├── loan_service.py    # Service crédit
│   ├── consent_service.py # Service consentements
│   ├── scoring_service.py # Service scoring
│   ├── audit_service.py   # Service audit
│   └── external_data_simulator.py # Simulateur Mobile Money
└── routers/
    ├── auth.py            # Routes authentification
    ├── loan.py            # Routes crédit
    ├── consent.py         # Routes consentements
    ├── scoring.py         # Routes scoring
    ├── wallet.py           # Routes portefeuille
    ├── audit.py           # Routes audit
    ├── health.py          # Health check
    └── ussd.py            # Routes USSD (Phase 1)
```

## 🚀 Démarrage

```bash
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source venv/bin/activate     # Linux/Mac

# Démarrer le serveur
uvicorn app.main:app --reload
```

Le serveur sera accessible sur `http://127.0.0.1:8000`

## 📚 Documentation API

Une fois le serveur démarré, accédez à :
- **Swagger UI** : `http://127.0.0.1:8000/docs`
- **ReDoc** : `http://127.0.0.1:8000/redoc`

## 🔄 Scénario complet de test

### 1. Créer un compte
```bash
POST /auth/register
{
  "msisdn": "+237123456789",
  "full_name": "Jean Dupont"
}
```

### 2. Définir le PIN
```bash
POST /auth/set-pin
{
  "msisdn": "+237123456789",
  "pin": "1234"
}
```

### 3. Accepter les consentements
```bash
# T&C
POST /consent/accept
{
  "msisdn": "+237123456789",
  "consent_type": "TERMS_AND_CONDITIONS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}

# Scoring
POST /consent/accept
{
  "msisdn": "+237123456789",
  "consent_type": "SCORING_DATA_ACCESS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```

### 4. Consulter l'offre de crédit
```bash
GET /scoring/+237123456789/offer
```

### 5. Demander un crédit
```bash
POST /loans/request
{
  "msisdn": "+237123456789",
  "pin": "1234",
  "amount": 50000,
  "duration_days": 30
}
```

### 6. Consulter le statut
```bash
GET /loans/{loan_id}/status?msisdn=+237123456789
```

### 7. Rembourser
```bash
POST /loans/repay
{
  "msisdn": "+237123456789",
  "pin": "1234",
  "loan_id": 1,
  "amount": 50000
}
```

### 8. Consulter l'historique
```bash
GET /loans/user/+237123456789/history
GET /audit/user/+237123456789/logs
```

## 🎯 Règles métier

### Scoring
- Score de base : 500 points
- Ajustements :
  - Ancienneté compte : 0-150 points
  - Fréquence utilisation : 0-100 points
  - Historique crédit : 0-150 points
  - Données externes : 0-100 points
- Score maximum : 1000 points
- Score minimum requis pour crédit : 400 points

### Plafonds de crédit
- Score ≥ 800 : 500 000 FCFA
- Score ≥ 700 : 300 000 FCFA
- Score ≥ 600 : 200 000 FCFA
- Score ≥ 500 : 100 000 FCFA
- Score ≥ 400 : 50 000 FCFA
- Score < 400 : 10 000 FCFA (crédit d'amorçage)

### Taux d'intérêt
- Premier crédit : 5%
- Crédits suivants : 3%

### Contraintes
- Un seul crédit actif par utilisateur
- PIN obligatoire pour demande et remboursement
- Consentements obligatoires avant demande
- Montant minimum : 1 000 FCFA
- Montant maximum : 1 000 000 FCFA

## 🔒 Sécurité

- PIN hashé avec bcrypt (jamais en clair)
- Validation stricte des entrées (Pydantic)
- Messages d'erreur non techniques pour l'utilisateur
- Audit trail complet

## 📊 Base de données

SQLite par défaut (fichier `fintech.db` à la racine).

Les tables sont créées automatiquement au démarrage :
- `users` : Utilisateurs
- `wallets` : Portefeuilles
- `loans` : Crédits
- `consents` : Consentements
- `audit_logs` : Logs d'audit
- `scoring_data` : Données de scoring

## 🔄 Données externes simulées

Le module `external_data_simulator.py` simule les données Mobile Money :
- Ancienneté du compte (mois)
- Volume mensuel moyen
- Nombre de transactions mensuelles
- Régularité d'activité

**En production**, ce module sera remplacé par un connecteur réel vers un fournisseur télécom.

## ✅ Definition of Done

Le backend permet une démo complète du scénario :
1. ✅ Création de compte
2. ✅ Acceptation des T&C
3. ✅ Définition du PIN
4. ✅ Demande de microcrédit
5. ✅ Décision + décaissement simulé
6. ✅ Consultation du statut
7. ✅ Remboursement
8. ✅ Historique cohérent et traçable

## 🎓 Points clés

- **Scoring explicable** : Chaque décision peut être expliquée
- **Traçabilité complète** : Tous les événements sont enregistrés
- **Architecture évolutive** : Prête pour industrialisation
- **Conformité bancaire** : Respect des exigences de traçabilité
- **Séparation des responsabilités** : Routes / Services / Modèles / Schémas

## 📝 Notes

- Le décaissement Mobile Money est **simulé** (pas de transaction réelle)
- Aucun wallet interne n'est géré (simulation uniquement)
- Les données externes sont **simulées** mais structurées pour un remplacement facile
- Pas de Machine Learning en Phase 2 (scoring déterministe)
