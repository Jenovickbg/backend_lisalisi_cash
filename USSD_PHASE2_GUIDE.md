# 📞 USSD Phase 2 - Lisalisi cash - Guide Complet

## 🎯 Vue d'ensemble

L'USSD est maintenant **complètement intégré** avec toutes les fonctionnalités Phase 2 !

**Nom du système** : **Lisalisi cash**

---

## ✅ Fonctionnalités disponibles via USSD

### 1. **Créer un compte** (Option 1)
- Création automatique avec le numéro de téléphone
- Pas besoin de nom complet via USSD

### 2. **Définir PIN** (Option 2)
- Saisie du PIN (4 chiffres)
- Confirmation du PIN
- Validation et hashage sécurisé

### 3. **Accepter T&C** (Option 3)
- Accepter les termes et conditions
- Accepter le consentement scoring
- Vérification des consentements existants

### 4. **Consulter offre de crédit** (Option 4)
- Affiche le score calculé
- Montant maximum autorisé
- Explication du score

### 5. **Demander crédit** (Option 5)
- Navigation : Montant → Durée → PIN
- Validation du montant (min 1000, max selon score)
- Choix de la durée (7, 14, 30, 60, 90 jours)
- Confirmation avec PIN
- Décision automatique (APPROVED/REJECTED)

### 6. **Rembourser crédit** (Option 6)
- Liste des crédits actifs
- Choix du crédit à rembourser
- Saisie du montant
- Confirmation avec PIN
- Mise à jour automatique

### 7. **Consulter historique** (Option 7)
- Liste des crédits (max 5)
- Statut de chaque crédit
- Montants et dates

---

## 📋 Menu Principal

```
CON Bienvenue sur Lisalisi cash
1. Creer un compte
2. Definir PIN
3. Accepter T&C
4. Consulter offre credit
5. Demander credit
6. Rembourser credit
7. Historique credits
0. Quitter
```

---

## 🧪 Scénarios de test

### Scénario 1 : Création de compte et PIN

**Étape 1** : Menu principal
```
POST /ussd
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": ""
}
```
**Réponse** : Menu principal

**Étape 2** : Créer compte
```
POST /ussd
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "1"
}
```
**Réponse** : `END Compte cree avec succes!`

**Étape 3** : Définir PIN
```
POST /ussd
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2"
}
```
**Réponse** : `CON Entrez votre PIN (4 chiffres):`

**Étape 4** : Saisir PIN
```
POST /ussd
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2*1234"
}
```
**Réponse** : `CON Confirmez votre PIN:`

**Étape 5** : Confirmer PIN
```
POST /ussd
{
  "sessionId": "test-1",
  "phoneNumber": "+237123456789",
  "text": "2*1234*1234"
}
```
**Réponse** : `END PIN defini avec succes!`

---

### Scénario 2 : Accepter T&C et demander crédit

**Étape 1** : Accepter T&C
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "3"
}
```
**Réponse** : Menu T&C

**Étape 2** : Accepter T&C
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "3*1"
}
```
**Réponse** : `END Consentement accepte avec succes!`

**Étape 3** : Accepter Scoring
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "3*2"
}
```
**Réponse** : `END Consentement accepte avec succes!`

**Étape 4** : Consulter offre
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "4"
}
```
**Réponse** : Score et montant max

**Étape 5** : Demander crédit
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "5"
}
```
**Réponse** : `CON Demande de credit\nEntrez le montant (FCFA):`

**Étape 6** : Saisir montant
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "5*50000"
}
```
**Réponse** : Menu durée

**Étape 7** : Choisir durée
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "5*50000*3"
}
```
**Réponse** : `CON Entrez votre PIN pour confirmer:`

**Étape 8** : Confirmer avec PIN
```
POST /ussd
{
  "sessionId": "test-2",
  "phoneNumber": "+237123456789",
  "text": "5*50000*3*1234"
}
```
**Réponse** : `END Credit approuve!` ou `END Credit refuse`

---

### Scénario 3 : Rembourser un crédit

**Étape 1** : Menu remboursement
```
POST /ussd
{
  "sessionId": "test-3",
  "phoneNumber": "+237123456789",
  "text": "6"
}
```
**Réponse** : Liste des crédits actifs

**Étape 2** : Choisir crédit
```
POST /ussd
{
  "sessionId": "test-3",
  "phoneNumber": "+237123456789",
  "text": "6*1"
}
```
**Réponse** : `CON Entrez le montant a rembourser:`

**Étape 3** : Saisir montant
```
POST /ussd
{
  "sessionId": "test-3",
  "phoneNumber": "+237123456789",
  "text": "6*1*50000"
}
```
**Réponse** : `CON Entrez votre PIN pour confirmer:`

**Étape 4** : Confirmer avec PIN
```
POST /ussd
{
  "sessionId": "test-3",
  "phoneNumber": "+237123456789",
  "text": "6*1*50000*1234"
}
```
**Réponse** : `END Remboursement effectue`

---

## 📊 Navigation USSD

### Format de navigation

Le système utilise le format standard USSD avec `*` comme séparateur :

- **Niveau 1** : `"1"` → Option 1 du menu principal
- **Niveau 2** : `"1*2"` → Option 1, puis sous-option 2
- **Niveau 3** : `"1*2*3"` → Option 1, sous-option 2, puis action 3
- **Niveau 4+** : `"1*2*3*4"` → Navigation plus profonde

### Exemples de navigation

| Action | Text USSD |
|--------|-----------|
| Menu principal | `""` |
| Créer compte | `"1"` |
| Définir PIN (menu) | `"2"` |
| Saisir PIN | `"2*1234"` |
| Confirmer PIN | `"2*1234*1234"` |
| Menu T&C | `"3"` |
| Accepter T&C | `"3*1"` |
| Demander crédit | `"5"` |
| Montant crédit | `"5*50000"` |
| Durée crédit | `"5*50000*3"` |
| PIN confirmation | `"5*50000*3*1234"` |

---

## 🔄 Intégration avec les services

L'USSD utilise maintenant tous les services Phase 2 :

- ✅ **AuthService** : Création compte, PIN
- ✅ **ConsentService** : Gestion T&C
- ✅ **ScoringService** : Calcul score et offre
- ✅ **LoanService** : Demande et remboursement crédit
- ✅ **AuditService** : Tous les événements sont tracés

---

## 🎯 Format des réponses

### CON (Continue)
La session continue, l'utilisateur peut faire un autre choix.

Exemple :
```
CON Entrez votre PIN (4 chiffres):
```

### END (Termine)
La session se termine.

Exemple :
```
END PIN defini avec succes!
```

---

## ⚠️ Validations

Le système valide :

- ✅ PIN : 4 chiffres uniquement
- ✅ Montant crédit : Min 1000, Max selon score
- ✅ Durée : 7, 14, 30, 60, 90 jours
- ✅ Consentements : Obligatoires avant demande crédit
- ✅ Crédit actif : Un seul crédit actif à la fois
- ✅ Montant remboursement : Min 100 FCFA

---

## 🧪 Comment tester

### Méthode 1 : Swagger UI

1. Démarrer : `uvicorn app.main:app --reload`
2. Ouvrir : `http://127.0.0.1:8000/docs`
3. Tester : POST /ussd avec différents text

### Méthode 2 : Postman

Utiliser la collection existante et modifier les valeurs de `text`

### Méthode 3 : Script Python

Créer un script qui simule la navigation complète

---

## 📝 Notes importantes

1. **Sessions USSD** : Chaque requête est indépendante (pas de session persistante)
2. **Navigation** : Les données sont passées dans le `text` avec `*`
3. **Compteur d'utilisation** : Mis à jour automatiquement à chaque requête
4. **Audit** : Tous les événements sont enregistrés avec channel="USSD"
5. **Erreurs** : Messages clairs et en français

---

## 🚀 Résultat final

Vous avez maintenant un **USSD complet** qui permet :

✅ Toutes les fonctionnalités Phase 2 accessibles via USSD  
✅ Navigation multi-niveaux intuitive  
✅ Intégration complète avec les services métier  
✅ Validation et sécurité  
✅ Messages en français  
✅ Compatible Africa's Talking  

**Le système USSD "Lisalisi cash" est opérationnel !** 🎉
