# 📱 Guide de Test - USSD vs Mobile App

## 🎯 Vue d'ensemble

Vous avez maintenant **2 canaux d'accès** à votre API :

1. **USSD** (non-smartphone) : Menu interactif via code USSD
2. **Mobile App** (smartphone) : API REST complète

---

## 📞 CANAL 1 : USSD (Menu Statique - Phase 1)

### Endpoint disponible

**POST `/ussd`** - Menu USSD compatible Africa's Talking

### Format de requête

```json
{
  "sessionId": "unique-session-id",
  "phoneNumber": "+237123456789",
  "text": ""
}
```

### Tests disponibles

#### Test 1 : Menu principal
```bash
POST http://127.0.0.1:8000/ussd
Content-Type: application/json

{
  "sessionId": "test-123",
  "phoneNumber": "+237123456789",
  "text": ""
}
```

**Réponse :**
```json
{
  "response": "CON Bienvenue au service Fintech\n1. Consulter le solde\n2. Autres options\n"
}
```

#### Test 2 : Option 1 (Consulter solde)
```bash
POST http://127.0.0.1:8000/ussd
Content-Type: application/json

{
  "sessionId": "test-123",
  "phoneNumber": "+237123456789",
  "text": "1"
}
```

**Réponse :**
```json
{
  "response": "END Votre solde: 1000 FCFA\nMerci d'avoir utilisé notre service."
}
```

#### Test 3 : Option invalide
```bash
POST http://127.0.0.1:8000/ussd
Content-Type: application/json

{
  "sessionId": "test-123",
  "phoneNumber": "+237123456789",
  "text": "99"
}
```

**Réponse :**
```json
{
  "response": "END Option invalide. Veuillez réessayer."
}
```

### ⚠️ État actuel USSD

- ✅ Menu statique fonctionnel
- ✅ Compatible Africa's Talking
- ⚠️ **Pas encore intégré avec les fonctionnalités Phase 2** (création compte, crédit, etc.)
- 📝 **À venir** : Intégration complète avec auth, loans, etc.

---

## 📲 CANAL 2 : Mobile App (API REST Complète - Phase 2)

### Endpoints disponibles

#### 🔐 Authentification (`/auth`)

| Méthode | Endpoint | Description |
|---------|---------|-------------|
| POST | `/auth/register` | Créer un compte |
| POST | `/auth/set-pin` | Définir le PIN |
| POST | `/auth/verify-pin` | Vérifier le PIN |
| GET | `/auth/user/{msisdn}` | Récupérer un utilisateur |

#### ✅ Consentements (`/consent`)

| Méthode | Endpoint | Description |
|---------|---------|-------------|
| POST | `/consent/accept` | Accepter un consentement |
| GET | `/consent/check/{msisdn}` | Vérifier les consentements |
| GET | `/consent/text/{consent_type}` | Lire le texte du consentement |

#### 📊 Scoring (`/scoring`)

| Méthode | Endpoint | Description |
|---------|---------|-------------|
| GET | `/scoring/{msisdn}/offer` | Consulter l'offre de crédit |

#### 💰 Crédits (`/loans`)

| Méthode | Endpoint | Description |
|---------|---------|-------------|
| POST | `/loans/request` | Demander un crédit |
| POST | `/loans/repay` | Rembourser un crédit |
| GET | `/loans/{loan_id}/status` | Statut d'un crédit |
| GET | `/loans/user/{msisdn}/history` | Historique des crédits |

#### 💳 Portefeuille (`/wallet`)

| Méthode | Endpoint | Description |
|---------|---------|-------------|
| GET | `/wallet/{msisdn}` | Consulter le portefeuille |

#### 📋 Audit (`/audit`)

| Méthode | Endpoint | Description |
|---------|---------|-------------|
| GET | `/audit/user/{msisdn}/logs` | Logs d'audit utilisateur |
| GET | `/audit/loan/{loan_id}/trail` | Trail d'audit d'un crédit |

#### 🏥 Health (`/health`)

| Méthode | Endpoint | Description |
|---------|---------|-------------|
| GET | `/health` | Vérifier que le service est opérationnel |

---

## 🧪 Comment tester

### Méthode 1 : Swagger UI (Recommandé)

1. **Démarrer le serveur :**
```bash
uvicorn app.main:app --reload
```

2. **Ouvrir Swagger :**
```
http://127.0.0.1:8000/docs
```

3. **Tester n'importe quel endpoint :**
   - Cliquer sur l'endpoint
   - Cliquer sur "Try it out"
   - Remplir les paramètres
   - Cliquer sur "Execute"

### Méthode 2 : Postman

1. **Importer la collection** `Postman_Collection_Fintech_USSD.json` (pour USSD)
2. **Créer une nouvelle collection "Mobile App"** avec les endpoints ci-dessus
3. **Tester chaque endpoint**

### Méthode 3 : PowerShell (Windows)

#### Exemple : Créer un compte
```powershell
$body = @{
    msisdn = "+237123456789"
    full_name = "Jean Dupont"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/auth/register" `
    -Method Post -Body $body -ContentType "application/json"
```

#### Exemple : Demander un crédit
```powershell
$body = @{
    msisdn = "+237123456789"
    pin = "1234"
    amount = 50000
    duration_days = 30
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/loans/request" `
    -Method Post -Body $body -ContentType "application/json"
```

---

## 📊 Comparaison USSD vs Mobile

| Fonctionnalité | USSD (Phase 1) | Mobile App (Phase 2) |
|----------------|---------------|---------------------|
| **Menu principal** | ✅ | ✅ (via endpoints) |
| **Création compte** | ❌ | ✅ `/auth/register` |
| **Définir PIN** | ❌ | ✅ `/auth/set-pin` |
| **Consentements** | ❌ | ✅ `/consent/accept` |
| **Scoring** | ❌ | ✅ `/scoring/{msisdn}/offer` |
| **Demander crédit** | ❌ | ✅ `/loans/request` |
| **Rembourser** | ❌ | ✅ `/loans/repay` |
| **Historique** | ❌ | ✅ `/loans/user/{msisdn}/history` |
| **Audit** | ❌ | ✅ `/audit/user/{msisdn}/logs` |

---

## 🎯 Scénario de test complet (Mobile App)

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
POST /consent/accept
{
  "msisdn": "+237123456789",
  "consent_type": "TERMS_AND_CONDITIONS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```

### 4. Consulter l'offre
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
GET /loans/1/status?msisdn=+237123456789
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

### 8. Voir l'historique
```bash
GET /loans/user/+237123456789/history
GET /audit/user/+237123456789/logs
```

---

## 📝 Résumé

### ✅ Ce que vous avez maintenant :

1. **USSD** : Menu statique fonctionnel (Phase 1)
   - 1 endpoint : `POST /ussd`
   - Menu interactif basique
   - Compatible Africa's Talking

2. **Mobile App** : API REST complète (Phase 2)
   - 20+ endpoints
   - Toutes les fonctionnalités métier
   - Authentification, crédits, scoring, audit

### 🔄 Pour tester :

1. **Swagger** : `http://127.0.0.1:8000/docs` (le plus simple)
2. **Postman** : Importer les collections
3. **PowerShell/curl** : Commandes ligne de commande

### 📚 Documentation :

- `PHASE2_README.md` : Documentation complète
- `SCENARIO_TEST_COMPLET.md` : Scénario détaillé
- `TEST_USSD.md` : Guide test USSD
- Ce fichier : Comparaison USSD vs Mobile

---

## 🚀 Prochaines étapes

Pour intégrer USSD avec les fonctionnalités Phase 2, il faudra :
- Modifier `/ussd` pour gérer les menus dynamiques
- Intégrer avec les services (auth, loan, etc.)
- Gérer la navigation USSD multi-niveaux

Mais pour l'instant, **vous avez une API REST complète fonctionnelle** pour l'application mobile ! 🎉
