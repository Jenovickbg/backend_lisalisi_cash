# Guide d'utilisation Postman pour tester l'endpoint USSD

## 📥 Importer la collection Postman

1. **Ouvrez Postman**
2. Cliquez sur **Import** (en haut à gauche)
3. Glissez-déposez le fichier `Postman_Collection_Fintech_USSD.json` OU cliquez sur "Upload Files" et sélectionnez le fichier
4. La collection "Fintech USSD API" apparaîtra dans votre sidebar gauche

## 🧪 Tester les différents cas

### Cas 1 : Menu Principal (text vide)
1. Dans la collection, cliquez sur **"1. Menu Principal (text vide)"**
2. Vérifiez que l'URL est : `http://127.0.0.1:8000/ussd`
3. Vérifiez que la méthode est **POST**
4. Cliquez sur **Send**
5. **Résultat attendu** : 
   ```json
   {
     "response": "CON Bienvenue au service Fintech\n1. Consulter le solde\n2. Autres options\n"
   }
   ```

### Cas 2 : Option 1 - Consulter Solde
1. Cliquez sur **"2. Option 1 - Consulter Solde"**
2. Cliquez sur **Send**
3. **Résultat attendu** :
   ```json
   {
     "response": "END Votre solde: 1000 FCFA\nMerci d'avoir utilisé notre service."
   }
   ```

### Cas 3 : Option Invalide
1. Cliquez sur **"3. Option Invalide"**
2. Cliquez sur **Send**
3. **Résultat attendu** :
   ```json
   {
     "response": "END Option invalide. Veuillez réessayer."
   }
   ```

### Bonus : Health Check
1. Cliquez sur **"Health Check"**
2. Cliquez sur **Send**
3. **Résultat attendu** :
   ```json
   {
     "status": "ok",
     "message": "Service opérationnel"
   }
   ```

## 🔄 Exécuter tous les tests en une fois

1. Cliquez avec le bouton droit sur la collection **"Fintech USSD API"**
2. Sélectionnez **"Run collection"**
3. Cliquez sur **Run Fintech USSD API**
4. Tous les tests s'exécuteront automatiquement et vous verrez les résultats

## 📝 Modifier les valeurs de test

Si vous voulez tester avec d'autres valeurs :

1. Cliquez sur une requête dans la collection
2. Allez dans l'onglet **Body**
3. Modifiez les valeurs dans le JSON :
   - `sessionId` : Identifiant de session (peut être n'importe quelle chaîne)
   - `phoneNumber` : Numéro de téléphone (format international recommandé)
   - `text` : Le texte de l'option USSD
     - `""` pour le menu principal
     - `"1"` pour l'option 1
     - `"99"` ou autre pour tester une option invalide

## ⚠️ Important

**Assurez-vous que le serveur est démarré avant de tester :**
```bash
uvicorn app.main:app --reload
```

## 🎯 Tests automatiques

Chaque requête contient des tests automatiques qui vérifient :
- Le code de statut HTTP (200)
- La présence de "CON" ou "END" dans la réponse
- Le contenu spécifique selon le cas

Vous pouvez voir les résultats des tests dans l'onglet **Test Results** après avoir envoyé une requête.
