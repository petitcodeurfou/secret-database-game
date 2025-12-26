# 📤 Comment mettre le projet sur GitHub

## ✅ État actuel

- ✅ Git initialisé
- ✅ 2 commits créés:
  1. Initial commit (jeu + React)
  2. Système d'authentification par code
- ✅ Branche `main` configurée
- ✅ Remote `origin` pointant vers: `https://github.com/petit-codeur-fou/secret-database-game.git`

## 🎯 Ce qu'il reste à faire

### Étape 1: Créer le repository sur GitHub

1. Allez sur **https://github.com/new**
2. Connectez-vous avec le compte **petit-codeur-fou**
3. Remplissez:
   - **Repository name**: `secret-database-game`
   - **Description**: `🎮 Jeu 2D avec passage secret vers interface React PostgreSQL - Code d'accès requis!`
   - **Visibilité**: **Public** ✅ (pour que tout le monde puisse y accéder)
   - **NE PAS COCHER** "Add a README file" (on l'a déjà)
   - **NE PAS COCHER** "Add .gitignore" (on l'a déjà)
4. Cliquez sur **"Create repository"**

### Étape 2: Pousser le code

Une fois le repo créé sur GitHub, exécutez dans ce dossier:

```bash
git push -u origin main
```

### Étape 3: Authentification

Vous devrez vous authentifier. **N'utilisez PAS votre mot de passe**, mais un **Personal Access Token**:

#### Créer un token:
1. Allez sur https://github.com/settings/tokens
2. Cliquez **"Generate new token (classic)"**
3. Nom du token: `Secret Database Game`
4. Cochez: **`repo`** (full control of private repositories)
5. Cliquez **"Generate token"**
6. **COPIEZ LE TOKEN** (vous ne le verrez qu'une fois!)

#### Utiliser le token:
Quand Git demande votre mot de passe, collez le **token** au lieu du mot de passe.

## 🌍 Accès depuis n'importe quel appareil

Une fois sur GitHub, n'importe qui pourra:

```bash
# Cloner le repo
git clone https://github.com/petit-codeur-fou/secret-database-game.git
cd secret-database-game

# Installer les dépendances Python
pip install -r requirements.txt

# Installer les dépendances React
cd database-ui
npm install
cd ..

# Créer les tables de test
python setup_database.py

# Terminal 1: API
python api.py

# Terminal 2: React
cd database-ui && npm start

# Terminal 3: Jeu
python game.py
```

## 🔐 Nouveau système avec code

Le jeu fonctionne maintenant comme ça:

1. **Trouvez le passage secret** → Un code s'affiche à l'écran (ex: `A3F9K2`)
2. **Le navigateur s'ouvre** automatiquement après 5 secondes
3. **Entrez le code** sur la page de login
4. **Accédez à la base de données** !

Le code **change à chaque fois** que vous entrez dans le passage secret!

## 📝 Ce qui a été ajouté

- ✅ Génération de code aléatoire (6 caractères)
- ✅ Affichage du code dans le jeu avec compte à rebours
- ✅ Sauvegarde du code dans `secret_code.json`
- ✅ API `/api/verify-code` pour vérifier le code
- ✅ Page de login React avec input stylisé
- ✅ Protection: impossible d'accéder aux données sans le bon code
- ✅ Le code change à chaque nouvelle entrée dans le passage

## 🎮 Testez maintenant!

Les 3 serveurs sont lancés:
- **API**: http://localhost:5000
- **React**: http://localhost:3000
- **Jeu**: Fenêtre Pygame

Jouez et trouvez le passage secret pour voir le système de code en action!
