# Guide de test de l'endpoint USSD

## Méthode 1 : Swagger UI (Recommandé - Interface graphique)

1. Démarrez le serveur :
```bash
uvicorn app.main:app --reload
```

2. Ouvrez votre navigateur : `http://127.0.0.1:8000/docs`

3. Cliquez sur **POST /ussd** → **Try it out**

4. Remplissez le body JSON avec :

**Test 1 - Menu principal :**
```json
{
  "sessionId": "test-session-123",
  "phoneNumber": "+237123456789",
  "text": ""
}
```

**Test 2 - Option 1 (Consulter solde) :**
```json
{
  "sessionId": "test-session-123",
  "phoneNumber": "+237123456789",
  "text": "1"
}
```

**Test 3 - Option invalide :**
```json
{
  "sessionId": "test-session-123",
  "phoneNumber": "+237123456789",
  "text": "99"
}
```

5. Cliquez sur **Execute** pour voir la réponse

---

## Méthode 2 : Script Python (test_ussd.py)

1. Installez requests si nécessaire :
```bash
pip install requests
```

2. Assurez-vous que le serveur est démarré

3. Exécutez le script :
```bash
python test_ussd.py
```

---

## Méthode 3 : cURL (Ligne de commande)

**Test 1 - Menu principal :**
```bash
curl -X POST "http://127.0.0.1:8000/ussd" \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\": \"test-123\", \"phoneNumber\": \"+237123456789\", \"text\": \"\"}"
```

**Test 2 - Option 1 :**
```bash
curl -X POST "http://127.0.0.1:8000/ussd" \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\": \"test-123\", \"phoneNumber\": \"+237123456789\", \"text\": \"1\"}"
```

**Test 3 - Option invalide :**
```bash
curl -X POST "http://127.0.0.1:8000/ussd" \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\": \"test-123\", \"phoneNumber\": \"+237123456789\", \"text\": \"99\"}"
```

---

## Méthode 4 : PowerShell (Invoke-RestMethod)

**Test 1 - Menu principal :**
```powershell
$body = @{
    sessionId = "test-123"
    phoneNumber = "+237123456789"
    text = ""
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/ussd" -Method Post -Body $body -ContentType "application/json"
```

**Test 2 - Option 1 :**
```powershell
$body = @{
    sessionId = "test-123"
    phoneNumber = "+237123456789"
    text = "1"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/ussd" -Method Post -Body $body -ContentType "application/json"
```

---

## Réponses attendues

### Menu principal (text="")
```json
{
  "response": "CON Bienvenue au service Fintech\n1. Consulter le solde\n2. Autres options\n"
}
```

### Option 1 (text="1")
```json
{
  "response": "END Votre solde: 1000 FCFA\nMerci d'avoir utilisé notre service."
}
```

### Option invalide (text="99")
```json
{
  "response": "END Option invalide. Veuillez réessayer."
}
```

---

## Format USSD (Africa's Talking)

- **CON** : Continue - La session continue, l'utilisateur peut faire un autre choix
- **END** : Termine - La session se termine
