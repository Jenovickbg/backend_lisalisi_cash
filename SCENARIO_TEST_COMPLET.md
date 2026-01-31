# Scénario de test complet - Phase 2

Ce document décrit un scénario de test end-to-end pour valider toutes les fonctionnalités du backend.

## Prérequis

1. Serveur démarré : `uvicorn app.main:app --reload`
2. Accès à Swagger : `http://127.0.0.1:8000/docs`
3. Ou utiliser Postman/curl

## Scénario : Utilisateur complet

### Étape 1 : Création de compte

**Requête :**
```bash
POST http://127.0.0.1:8000/auth/register
Content-Type: application/json

{
  "msisdn": "+237123456789",
  "full_name": "Jean Dupont"
}
```

**Réponse attendue :**
```json
{
  "id": 1,
  "msisdn": "+237123456789",
  "full_name": "Jean Dupont",
  "has_pin": false,
  "created_at": "2026-01-31T12:00:00"
}
```

### Étape 2 : Définir le PIN

**Requête :**
```bash
POST http://127.0.0.1:8000/auth/set-pin
Content-Type: application/json

{
  "msisdn": "+237123456789",
  "pin": "1234"
}
```

**Réponse attendue :**
```json
{
  "message": "PIN défini avec succès"
}
```

### Étape 3 : Accepter les termes et conditions

**Requête 1 - T&C :**
```bash
POST http://127.0.0.1:8000/consent/accept
Content-Type: application/json

{
  "msisdn": "+237123456789",
  "consent_type": "TERMS_AND_CONDITIONS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```

**Requête 2 - Scoring :**
```bash
POST http://127.0.0.1:8000/consent/accept
Content-Type: application/json

{
  "msisdn": "+237123456789",
  "consent_type": "SCORING_DATA_ACCESS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```

### Étape 4 : Vérifier les consentements

**Requête :**
```bash
GET http://127.0.0.1:8000/consent/check/+237123456789
```

**Réponse attendue :**
```json
{
  "has_terms_consent": true,
  "has_scoring_consent": true,
  "can_request_loan": true,
  "message": "Consentements complets"
}
```

### Étape 5 : Consulter l'offre de crédit

**Requête :**
```bash
GET http://127.0.0.1:8000/scoring/+237123456789/offer
```

**Réponse attendue :**
```json
{
  "score": 500.0,
  "score_version": "1.0",
  "max_loan_amount": 10000,
  "is_first_loan": true,
  "explanation": "Score de base - Profil en construction."
}
```

### Étape 6 : Demander un crédit

**Requête :**
```bash
POST http://127.0.0.1:8000/loans/request
Content-Type: application/json

{
  "msisdn": "+237123456789",
  "pin": "1234",
  "amount": 10000,
  "duration_days": 30
}
```

**Réponse attendue (si approuvé) :**
```json
{
  "loan_id": 1,
  "decision": "APPROVED",
  "amount_approved": 10500,
  "due_date": "2026-03-02T12:00:00",
  "decision_reason": "Crédit approuvé. Score: 500, Montant autorisé: 10000 FCFA",
  "score": 500.0,
  "score_explanation": "Score de base - Profil en construction."
}
```

### Étape 7 : Consulter le statut du crédit

**Requête :**
```bash
GET http://127.0.0.1:8000/loans/1/status?msisdn=+237123456789
```

**Réponse attendue :**
```json
{
  "loan_id": 1,
  "status": "ACTIVE",
  "amount_requested": 10000,
  "amount_approved": 10500,
  "amount_remaining": 10500,
  "due_date": "2026-03-02T12:00:00",
  "days_remaining": 30,
  "is_overdue": false
}
```

### Étape 8 : Rembourser le crédit

**Requête (remboursement total) :**
```bash
POST http://127.0.0.1:8000/loans/repay
Content-Type: application/json

{
  "msisdn": "+237123456789",
  "pin": "1234",
  "loan_id": 1,
  "amount": 10500
}
```

**Réponse attendue :**
```json
{
  "loan_id": 1,
  "amount_paid": 10500,
  "amount_remaining": 0,
  "is_fully_repaid": true,
  "message": "Crédit entièrement remboursé"
}
```

### Étape 9 : Consulter l'historique

**Requête 1 - Historique des crédits :**
```bash
GET http://127.0.0.1:8000/loans/user/+237123456789/history
```

**Requête 2 - Logs d'audit :**
```bash
GET http://127.0.0.1:8000/audit/user/+237123456789/logs
```

**Requête 3 - Trail d'audit du crédit :**
```bash
GET http://127.0.0.1:8000/audit/loan/1/trail
```

## Scénarios d'erreur à tester

### 1. Crédit sans consentements
- Créer un compte
- Essayer de demander un crédit sans accepter les T&C
- **Attendu** : Erreur "Les consentements requis ne sont pas acceptés"

### 2. PIN incorrect
- Créer un compte et définir un PIN
- Essayer de demander un crédit avec un PIN incorrect
- **Attendu** : Erreur "PIN incorrect"

### 3. Montant trop élevé
- Consulter l'offre de crédit (ex: max_loan_amount = 10000)
- Demander un crédit de 50000
- **Attendu** : Erreur "Montant demandé dépasse le plafond"

### 4. Crédit actif existant
- Demander un premier crédit (approuvé)
- Essayer de demander un deuxième crédit
- **Attendu** : Erreur "Un crédit est déjà actif"

### 5. Remboursement montant incorrect
- Avoir un crédit actif de 10000
- Essayer de rembourser 20000
- **Attendu** : Erreur "Le montant dépasse le montant restant"

## Tests avec Postman

1. Importer la collection `Postman_Collection_Fintech_USSD.json` (Phase 1)
2. Créer une nouvelle collection "Phase 2" avec les requêtes ci-dessus
3. Exécuter la collection dans l'ordre

## Tests avec curl (PowerShell)

```powershell
# 1. Créer compte
$body = @{msisdn="+237123456789"; full_name="Jean Dupont"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/auth/register" -Method Post -Body $body -ContentType "application/json"

# 2. Définir PIN
$body = @{msisdn="+237123456789"; pin="1234"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/auth/set-pin" -Method Post -Body $body -ContentType "application/json"

# 3. Accepter T&C
$body = @{msisdn="+237123456789"; consent_type="TERMS_AND_CONDITIONS"; version="1.0"; channel="APP"; accepted=$true} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/consent/accept" -Method Post -Body $body -ContentType "application/json"

# 4. Consulter offre
Invoke-RestMethod -Uri "http://127.0.0.1:8000/scoring/+237123456789/offer" -Method Get

# 5. Demander crédit
$body = @{msisdn="+237123456789"; pin="1234"; amount=10000; duration_days=30} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/loans/request" -Method Post -Body $body -ContentType "application/json"
```

## Validation finale

Après avoir exécuté le scénario complet, vérifier :

1. ✅ Le compte utilisateur existe
2. ✅ Le PIN est défini et fonctionne
3. ✅ Les consentements sont enregistrés
4. ✅ Le score est calculé
5. ✅ Le crédit est créé avec décision
6. ✅ Le statut du crédit est consultable
7. ✅ Le remboursement fonctionne
8. ✅ L'historique est complet
9. ✅ Les logs d'audit contiennent tous les événements

## Notes

- Les montants sont en FCFA
- Les dates sont en UTC
- Le scoring est déterministe (même MSISDN = même score)
- Les données externes sont simulées mais cohérentes
