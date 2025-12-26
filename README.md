# 🎮 Secret Database Game

Un jeu de plateforme 2D style Hollow Knight avec un passage secret menant à une interface de gestion de base de données PostgreSQL en React!

## 🎯 Concept

- **Jeu principal**: Plateforme 2D avec Pygame
- **Objectif visible**: Atteindre le drapeau "Level 2"
- **Secret caché**: Passage discret vers une interface de base de données
- **Interface React**: Gestion CRUD complète style Google Drive

## 🚀 Installation

### Prérequis
- Python 3.13+
- Node.js 18+
- PostgreSQL (Neon DB)

### 1. Cloner le repo
```bash
git clone https://github.com/petit-codeur-fou/secret-database-game.git
cd secret-database-game
```

### 2. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 3. Installer les dépendances React
```bash
cd database-ui
npm install
cd ..
```

### 4. Configurer la base de données
Créez les tables de test:
```bash
python setup_database.py
```

## 🎮 Lancement

Vous avez besoin de **3 terminaux**:

### Terminal 1: API Backend
```bash
python api.py
```

### Terminal 2: Interface React
```bash
cd database-ui
npm start
```

### Terminal 3: Jeu
```bash
python game.py
```

## 🕹️ Comment jouer

### Contrôles
- **A/D** ou **Flèches gauche/droite**: Déplacer
- **Espace** ou **W** ou **Flèche haut**: Sauter
- **ESC**: Quitter

### Objectif principal
1. Montez les plateformes en zigzag (côté gauche)
2. Atteignez le **drapeau rouge "Level 2"** en haut à gauche
3. Victoire!

### Passage secret 🤫
1. Explorez vers la **droite** du niveau
2. Montez sur la plateforme en haut à droite
3. Continuez jusqu'au **bord droit de l'écran**
4. Appuyez sur **→** pour entrer
5. Votre navigateur s'ouvre sur l'interface React!

## 💾 Interface de base de données

L'interface React offre:
- ✅ Vue dossiers style Google Drive
- ✅ Affichage des tables PostgreSQL
- ✅ Créer des lignes (INSERT)
- ✅ Modifier des lignes (UPDATE)
- ✅ Supprimer des lignes (DELETE)
- ✅ Interface moderne et responsive

## 📁 Structure du projet

```
.
├── game.py              # Jeu principal Pygame
├── player.py            # Logique du joueur
├── level.py             # Niveau 1 avec passage secret
├── api.py               # API Flask REST
├── setup_database.py    # Script de création des tables
├── requirements.txt     # Dépendances Python
├── database-ui/         # Application React
│   ├── src/
│   │   ├── App.js      # Composant principal
│   │   └── App.css     # Styles
│   └── package.json
└── README.md
```

## 🔧 Technologies

- **Jeu**: Python, Pygame
- **Backend**: Flask, PostgreSQL (Neon)
- **Frontend**: React, Axios
- **Base de données**: PostgreSQL

## 🎨 Fonctionnalités

- Physique de plateforme fluide
- Niveau avec plusieurs plateformes
- Passage secret totalement discret
- API REST complète
- Interface CRUD moderne
- Connexion PostgreSQL réelle

## 📝 License

MIT

## 👤 Auteur

**petit-codeur-fou**

---

🎮 Bon jeu et bonne exploration de la base de données secrète!
