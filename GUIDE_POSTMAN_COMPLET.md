# 📮 Guide Complet - Tester avec Postman

## 🚀 Étape 1 : Préparer Postman

### 1. Ouvrir Postman
- Téléchargez Postman si ce n'est pas déjà fait : https://www.postman.com/downloads/
- Ouvrez Postman

### 2. Vérifier que le serveur est démarré
Dans un terminal PowerShell :
```powershell
cd C:\Users\HP\Desktop\hackathon\backend
uvicorn app.main:app --reload
```

Vous devriez voir : `INFO:     Uvicorn running on http://127.0.0.1:8000`

---

## 📞 PARTIE 1 : Tester l'USSD

### Test 1 : Menu Principal

1. **Créer une nouvelle requête** dans Postman
2. **Méthode** : `POST`
3. **URL** : `http://127.0.0.1:8000/ussd`
4. **Headers** :
   - Cliquez sur "Headers"
   - Ajoutez : `Content-Type` = `application/json`
5. **Body** :
   - Sélectionnez "raw"
   - Choisissez "JSON" dans le menu déroulant
   - Collez ce JSON :
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": ""
}
```
6. **Cliquez "Send"**

**Résultat attendu :**
```json
{
  "response": "CON Bienvenue sur Lisalisi cash\n1. Creer un compte\n2. Definir PIN\n3. Accepter T&C\n4. Consulter offre credit\n5. Demander credit\n6. Rembourser credit\n7. Historique credits\n0. Quitter"
}
```

---

### Test 2 : Créer un compte

**Même requête, changez juste le body :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "1"
}
```

**Résultat attendu :**
```json
{
  "response": "END Compte cree avec succes!\nNumero: +237123456789\nDefinissez votre PIN (option 2)"
}
```

---

### Test 3 : Définir PIN (Étape 1 - Menu)

**Body :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2"
}
```

**Résultat :** `CON Entrez votre PIN (4 chiffres):`

---

### Test 4 : Définir PIN (Étape 2 - Saisir PIN)

**Body :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2*1234"
}
```

**Résultat :** `CON Confirmez votre PIN:`

---

### Test 5 : Définir PIN (Étape 3 - Confirmer)

**Body :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2*1234*1234"
}
```

**Résultat :** `END PIN defini avec succes!`

---

### Test 6 : Accepter T&C

**Étape 1 - Menu T&C :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "3"
}
```

**Étape 2 - Accepter T&C :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "3*1"
}
```

**Étape 3 - Accepter Scoring :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "3*2"
}
```

---

### Test 7 : Consulter offre de crédit

**Body :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "4"
}
```

**Résultat :** Score et montant maximum

---

### Test 8 : Demander un crédit (Navigation complète)

**Étape 1 - Menu demande :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "5"
}
```

**Étape 2 - Saisir montant :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "5*50000"
}
```

**Étape 3 - Choisir durée (3 = 30 jours) :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "5*50000*3"
}
```

**Étape 4 - Confirmer avec PIN :**
```json
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "5*50000*3*1234"
}
```

**Résultat :** `END Credit approuve!` ou `END Credit refuse`

---

## 📱 PARTIE 2 : Tester l'API Mobile

### Test 1 : Créer un compte

1. **Nouvelle requête** dans Postman
2. **Méthode** : `POST`
3. **URL** : `http://127.0.0.1:8000/auth/register`
4. **Headers** : `Content-Type` = `application/json`
5. **Body** (raw JSON) :
```json
{
  "msisdn": "+237123456789",
  "full_name": "Jean Dupont"
}
```
6. **Send**

**Résultat attendu :**
```json
{
  "id": 1,
  "msisdn": "+237123456789",
  "full_name": "Jean Dupont",
  "has_pin": false,
  "created_at": "2026-01-31T..."
}
```

---

### Test 2 : Définir le PIN

1. **Nouvelle requête**
2. **Méthode** : `POST`
3. **URL** : `http://127.0.0.1:8000/auth/set-pin`
4. **Headers** : `Content-Type` = `application/json`
5. **Body** :
```json
{
  "msisdn": "+237123456789",
  "pin": "1234"
}
```
6. **Send**

**Résultat :** `{"message": "PIN défini avec succès"}`

---

### Test 3 : Vérifier le PIN

1. **Nouvelle requête**
2. **Méthode** : `POST`
3. **URL** : `http://127.0.0.1:8000/auth/verify-pin`
4. **Body** :
```json
{
  "msisdn": "+237123456789",
  "pin": "1234"
}
```
5. **Send**

**Résultat :** `{"valid": true, "message": "PIN correct"}`

---

### Test 4 : Accepter T&C (1ère fois)

1. **Nouvelle requête**
2. **Méthode** : `POST`
3. **URL** : `http://127.0.0.1:8000/consent/accept`
4. **Body** :
```json
{
  "msisdn": "+237123456789",
  "consent_type": "TERMS_AND_CONDITIONS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```
5. **Send**

---

### Test 5 : Accepter Scoring

**Même requête, changez le body :**
```json
{
  "msisdn": "+237123456789",
  "consent_type": "SCORING_DATA_ACCESS",
  "version": "1.0",
  "channel": "APP",
  "accepted": true
}
```

---

### Test 6 : Vérifier les consentements

1. **Nouvelle requête**
2. **Méthode** : `GET`
3. **URL** : `http://127.0.0.1:8000/consent/check/+237123456789`
4. **Send** (pas de body pour GET)

**Résultat :**
```json
{
  "has_terms_consent": true,
  "has_scoring_consent": true,
  "can_request_loan": true,
  "message": "Consentements complets"
}
```

---

### Test 7 : Consulter l'offre de crédit

1. **Nouvelle requête**
2. **Méthode** : `GET`
3. **URL** : `http://127.0.0.1:8000/scoring/+237123456789/offer`
4. **Send**

**Résultat :**
```json
{
  "score": 500.0,
  "score_version": "1.0",
  "max_loan_amount": 10000,
  "is_first_loan": true,
  "explanation": "Score de base - Profil en construction."
}
```

---

### Test 8 : Demander un crédit

1. **Nouvelle requête**
2. **Méthode** : `POST`
3. **URL** : `http://127.0.0.1:8000/loans/request`
4. **Body** :
```json
{
  "msisdn": "+237123456789",
  "pin": "1234",
  "amount": 50000,
  "duration_days": 30
}
```
5. **Send**

**Résultat :**
```json
{
  "loan_id": 1,
  "decision": "APPROVED",
  "amount_approved": 52500,
  "due_date": "2026-03-02T...",
  "decision_reason": "Crédit approuvé...",
  "score": 500.0,
  "score_explanation": "..."
}
```

---

### Test 9 : Consulter le statut d'un crédit

1. **Nouvelle requête**
2. **Méthode** : `GET`
3. **URL** : `http://127.0.0.1:8000/loans/1/status?msisdn=+237123456789`
   (Remplacez `1` par l'ID du crédit créé)
4. **Send**

---

### Test 10 : Rembourser un crédit

1. **Nouvelle requête**
2. **Méthode** : `POST`
3. **URL** : `http://127.0.0.1:8000/loans/repay`
4. **Body** :
```json
{
  "msisdn": "+237123456789",
  "pin": "1234",
  "loan_id": 1,
  "amount": 52500
}
```
5. **Send**

**Résultat :**
```json
{
  "loan_id": 1,
  "amount_paid": 52500,
  "amount_remaining": 0,
  "is_fully_repaid": true,
  "message": "Crédit entièrement remboursé"
}
```

---

### Test 11 : Consulter l'historique

1. **Nouvelle requête**
2. **Méthode** : `GET`
3. **URL** : `http://127.0.0.1:8000/loans/user/+237123456789/history`
4. **Send**

---

### Test 12 : Voir les logs d'audit

1. **Nouvelle requête**
2. **Méthode** : `GET`
3. **URL** : `http://127.0.0.1:8000/audit/user/+237123456789/logs`
4. **Send**

---

## 💡 Astuces Postman

### 1. Créer une Collection

1. Cliquez sur "New" → "Collection"
2. Nommez-la "Lisalisi cash API"
3. Glissez vos requêtes dans la collection
4. Organisez par dossiers : "USSD", "Auth", "Loans", etc.

### 2. Utiliser des Variables

1. Cliquez sur l'icône "Variables" de la collection
2. Ajoutez :
   - `base_url` = `http://127.0.0.1:8000`
   - `msisdn` = `+237123456789`
   - `pin` = `1234`
3. Dans vos URLs, utilisez : `{{base_url}}/ussd`
4. Dans vos bodies, utilisez : `"msisdn": "{{msisdn}}"`

### 3. Sauvegarder les réponses

1. Après avoir envoyé une requête
2. Cliquez sur "Save Response"
3. Nommez-la (ex: "Menu principal USSD")

### 4. Tests automatiques

Dans l'onglet "Tests" de chaque requête, ajoutez :

```javascript
// Vérifier le statut
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Vérifier le contenu
pm.test("Response has response field", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('response');
});
```

---

## 📋 Checklist de test Postman

### USSD
- [ ] Menu principal s'affiche
- [ ] Création compte fonctionne
- [ ] Définition PIN (3 étapes) fonctionne
- [ ] Acceptation T&C fonctionne
- [ ] Consultation offre fonctionne
- [ ] Demande crédit (4 étapes) fonctionne
- [ ] Remboursement fonctionne
- [ ] Historique s'affiche

### Mobile App
- [ ] Création compte fonctionne
- [ ] Définition PIN fonctionne
- [ ] Vérification PIN fonctionne
- [ ] Acceptation T&C fonctionne
- [ ] Vérification consentements fonctionne
- [ ] Consultation offre fonctionne
- [ ] Demande crédit fonctionne
- [ ] Statut crédit fonctionne
- [ ] Remboursement fonctionne
- [ ] Historique fonctionne
- [ ] Audit logs fonctionnent

---

## 🎯 Scénario complet dans Postman

### Scénario USSD complet

1. Menu principal → `text: ""`
2. Créer compte → `text: "1"`
3. Définir PIN → `text: "2"` → `text: "2*1234"` → `text: "2*1234*1234"`
4. Accepter T&C → `text: "3"` → `text: "3*1"` → `text: "3*2"`
5. Consulter offre → `text: "4"`
6. Demander crédit → `text: "5"` → `text: "5*50000"` → `text: "5*50000*3"` → `text: "5*50000*3*1234"`

### Scénario Mobile complet

1. POST `/auth/register`
2. POST `/auth/set-pin`
3. POST `/consent/accept` (2 fois)
4. GET `/scoring/{msisdn}/offer`
5. POST `/loans/request`
6. GET `/loans/{id}/status`
7. POST `/loans/repay`
8. GET `/loans/user/{msisdn}/history`

---

## ✅ C'est parti !

1. **Démarrez le serveur** (terminal PowerShell)
2. **Ouvrez Postman**
3. **Créez vos requêtes** en suivant ce guide
4. **Testez !**

**Tous les exemples de body JSON sont prêts à copier-coller !** 🚀
