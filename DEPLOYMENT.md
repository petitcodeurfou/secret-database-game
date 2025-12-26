# 🌐 Guide de déploiement web

Ce guide explique comment héberger le jeu sur internet pour que n'importe qui puisse jouer sans rien installer!

## 📋 Architecture

Le projet se compose de 3 parties qui doivent être hébergées séparément :

1. **🎮 Jeu Pygame** → GitHub Pages ou itch.io (version web avec Pygbag)
2. **🔌 API Flask** → Render.com (gratuit)
3. **💻 Interface React** → Vercel (gratuit)

---

## 1️⃣ Héberger l'API Flask sur Render

### Étape 1 : Créer un compte
- Allez sur https://render.com
- Créez un compte (gratuit)

### Étape 2 : Déployer l'API
1. Cliquez sur **"New +"** → **"Web Service"**
2. Connectez votre repo GitHub : `https://github.com/petitcodeurfou/secret-database-game`
3. Configurez :
   - **Name** : `secret-database-api`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn api:app`
   - **Plan** : Free
4. Cliquez **"Create Web Service"**

### Étape 3 : Notez l'URL
Une fois déployé, vous aurez une URL comme :
```
https://secret-database-api.onrender.com
```

**⚠️ Important** : Notez cette URL, vous en aurez besoin!

---

## 2️⃣ Héberger l'interface React sur Vercel

### Étape 1 : Préparer le code
Vous devez modifier `database-ui/src/App.js` pour utiliser l'URL de l'API :

```javascript
// Remplacez cette ligne :
const API_URL = 'http://localhost:5000/api';

// Par :
const API_URL = 'https://secret-database-api.onrender.com/api';
```

### Étape 2 : Déployer sur Vercel
1. Allez sur https://vercel.com
2. Créez un compte (gratuit)
3. Cliquez sur **"Add New..." → "Project"**
4. Importez le repo : `https://github.com/petitcodeurfou/secret-database-game`
5. Configurez :
   - **Framework Preset** : Create React App
   - **Root Directory** : `database-ui`
   - **Build Command** : `npm run build`
   - **Output Directory** : `build`
6. Cliquez **"Deploy"**

### Étape 3 : Notez l'URL
Vous obtiendrez une URL comme :
```
https://secret-database-game.vercel.app
```

---

## 3️⃣ Héberger le jeu sur itch.io

### Option A : Version Web avec Pygbag (Recommandé)

**Préparer le jeu :**
```bash
# Installer pygbag si pas déjà fait
pip install pygbag

# Construire la version web
pygbag --build .
```

Cela créera un dossier `build/web` avec des fichiers HTML.

**Uploader sur itch.io :**
1. Allez sur https://itch.io
2. Créez un compte
3. Allez sur **Dashboard → Create new project**
4. Configurez :
   - **Title** : Secret Database Game
   - **Kind of project** : HTML
   - **Uploads** : Uploadez le dossier `build/web` en ZIP
   - **This file will be played in the browser** : ✅ Cochez
5. Publiez!

### Option B : Lien vers téléchargement GitHub

Si Pygbag ne fonctionne pas, vous pouvez simplement :
1. Créer un projet itch.io
2. Mettre le lien GitHub dans la description
3. Les joueurs téléchargent et installent manuellement

---

## 🔗 Configuration finale

Une fois tout hébergé, vous aurez :

- **Jeu** : `https://petitcodeurfou.itch.io/secret-database-game`
- **Interface Base de données** : `https://secret-database-game.vercel.app`
- **API** : `https://secret-database-api.onrender.com`

### Instructions pour les joueurs :

1. Allez sur le jeu itch.io
2. Jouez et trouvez le passage secret
3. Notez le code affiché à l'écran
4. Allez sur `https://secret-database-game.vercel.app`
5. Entrez le code
6. Accédez à la base de données secrète! 🎉

---

## 🔒 Sécurité du secret

Le code est obscurci avec base64, donc même si quelqu'un regarde le code source sur GitHub, les coordonnées du passage secret ne sont pas évidentes :

```python
# Au lieu de voir :
self.secret_passage_rect = pygame.Rect(1250, 200, 50, 70)

# Ils verront :
self._sc = base64.b64decode(b'MTI1MCwyMDAsNTAsNzA=').decode().split(',')
self.secret_passage_rect = pygame.Rect(int(self._sc[0]), int(self._sc[1]), ...)
```

---

## 📝 Notes

- **Render free tier** : L'API s'endort après 15 min d'inactivité (redémarre au premier accès, ~30 secondes)
- **Vercel** : Pas de limite, toujours rapide
- **itch.io** : Parfait pour les jeux HTML5

Tout est 100% gratuit! 🎮✨
