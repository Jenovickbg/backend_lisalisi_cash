# 🚀 Guide de Démarrage Rapide - Comment Tester

## 📋 Étape 1 : Démarrer le serveur

### Ouvrir un terminal PowerShell

```powershell
# Aller dans le dossier backend
cd C:\Users\HP\Desktop\hackathon\backend

# Activer l'environnement virtuel (si pas déjà fait)
.\venv\Scripts\Activate.ps1

# Démarrer le serveur
uvicorn app.main:app --reload
```

**Vous devriez voir :**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Le serveur est maintenant accessible sur `http://127.0.0.1:8000`**

---

## 📖 Étape 2 : Ouvrir Swagger (Interface de test)

### Dans votre navigateur, ouvrez :

```
http://127.0.0.1:8000/docs
```

**Vous verrez la documentation interactive Swagger avec tous les endpoints !**

---

## 🧪 Étape 3 : Tester l'USSD

### Option A : Via Swagger (Recommandé)

1. Dans Swagger, trouvez **POST /ussd**
2. Cliquez sur **"Try it out"**
3. Remplissez le body JSON :

**Test 1 - Menu principal :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": ""
}
```
4. Cliquez sur **"Execute"**
5. Vous verrez le menu "Lisalisi cash" !

**Test 2 - Créer un compte :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "1"
}
```

**Test 3 - Définir PIN :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2"
}
```
Puis :
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2*1234"
}
```
Puis :
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2*1234*1234"
}
```

### Option B : Via PowerShell

Ouvrez un **nouveau terminal PowerShell** (gardez le serveur en cours d'exécution) :

```powershell
# Test menu principal
$body = @{
    sessionId = "test-1"
    phoneNumber = "+237123456789"
    text = ""
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/ussd" `
    -Method Post -Body $body -ContentType "application/json"
```

---

## 📱 Étape 4 : Tester l'API Mobile

### Scénario complet dans Swagger

#### 1. Créer un compte

**Endpoint :** `POST /auth/register`

**Body :**
```json
{
  "msisdn": "+237123456789",
  "full_name": "Jean Dupont"
}
```

**Cliquez "Execute"** → Vous verrez le compte créé !

#### 2. Définir le PIN

**Endpoint :** `POST /auth/set-pin`

**Body :**
```json
{
  "msisdn": "+237123456789",
  "pin": "1234"
}
```

#### 3. Accepter les T&C

**Endpoint :** `POST /consent/accept`

**Body 1 - T&C :**
```json
{
  "msisdn": "+237123456789",
  "consent_type": "TERMS_AND_CONDITIONS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```

**Body 2 - Scoring :**
```json
{
  "msisdn": "+237123456789",
  "consent_type": "SCORING_DATA_ACCESS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```

#### 4. Consulter l'offre de crédit

**Endpoint :** `GET /scoring/+237123456789/offer`

**Cliquez "Execute"** → Vous verrez le score et le montant max !

#### 5. Demander un crédit

**Endpoint :** `POST /loans/request`

**Body :**
```json
{
  "msisdn": "+237123456789",
  "pin": "1234",
  "amount": 50000,
  "duration_days": 30
}
```

**Cliquez "Execute"** → Vous verrez la décision (APPROVED ou REJECTED) !

#### 6. Consulter le statut

**Endpoint :** `GET /loans/1/status?msisdn=+237123456789`

(Remplacez `1` par l'ID du crédit créé)

#### 7. Rembourser

**Endpoint :** `POST /loans/repay`

**Body :**
```json
{
  "msisdn": "+237123456789",
  "pin": "1234",
  "loan_id": 1,
  "amount": 50000
}
```

#### 8. Voir l'historique

**Endpoint :** `GET /loans/user/+237123456789/history`

**Endpoint :** `GET /audit/user/+237123456789/logs`

---

## 🎯 Scénario de test rapide (5 minutes)

### Test USSD complet

1. **Menu principal** : `text = ""`
2. **Créer compte** : `text = "1"`
3. **Définir PIN** : `text = "2"` → `text = "2*1234"` → `text = "2*1234*1234"`
4. **Accepter T&C** : `text = "3"` → `text = "3*1"` → `text = "3*2"`
5. **Consulter offre** : `text = "4"`
6. **Demander crédit** : `text = "5"` → `text = "5*50000"` → `text = "5*50000*3"` → `text = "5*50000*3*1234"`

### Test Mobile App complet

1. **POST /auth/register** → Créer compte
2. **POST /auth/set-pin** → Définir PIN
3. **POST /consent/accept** (2 fois) → Accepter T&C
4. **GET /scoring/{msisdn}/offer** → Voir offre
5. **POST /loans/request** → Demander crédit
6. **GET /loans/{id}/status** → Voir statut
7. **POST /loans/repay** → Rembourser

---

## 📝 Checklist de test

### USSD
- [ ] Menu principal s'affiche
- [ ] Création de compte fonctionne
- [ ] Définition PIN fonctionne
- [ ] Acceptation T&C fonctionne
- [ ] Consultation offre fonctionne
- [ ] Demande crédit fonctionne
- [ ] Remboursement fonctionne
- [ ] Historique s'affiche

### Mobile App
- [ ] Création compte fonctionne
- [ ] Définition PIN fonctionne
- [ ] Vérification PIN fonctionne
- [ ] Acceptation T&C fonctionne
- [ ] Consultation offre fonctionne
- [ ] Demande crédit fonctionne
- [ ] Statut crédit fonctionne
- [ ] Remboursement fonctionne
- [ ] Historique fonctionne
- [ ] Audit logs fonctionnent

---

## 🔧 En cas de problème

### Le serveur ne démarre pas

```powershell
# Vérifier que vous êtes dans le bon dossier
cd C:\Users\HP\Desktop\hackathon\backend

# Vérifier que le venv est activé
.\venv\Scripts\Activate.ps1

# Réinstaller les dépendances si nécessaire
pip install -r requirements.txt

# Redémarrer
uvicorn app.main:app --reload
```

### Erreur "Module not found"

```powershell
# Installer les dépendances
pip install -r requirements.txt
```

### Erreur de base de données

La base de données SQLite sera créée automatiquement au premier démarrage dans le fichier `fintech.db` à la racine du projet.

---

## 📚 Documentation complète

Pour plus de détails, consultez :

1. **USSD_PHASE2_GUIDE.md** - Guide complet USSD
2. **SCENARIO_TEST_COMPLET.md** - Scénarios détaillés
3. **RESUME_COMPLET_USSD_ET_MOBILE.md** - Résumé complet
4. **Swagger UI** - `http://127.0.0.1:8000/docs` (le plus pratique !)

---

## ✅ C'est parti !

1. **Démarrez le serveur** (Étape 1)
2. **Ouvrez Swagger** (Étape 2)
3. **Testez !** (Étape 3 ou 4)

**Swagger est votre meilleur ami pour tester rapidement !** 🚀
