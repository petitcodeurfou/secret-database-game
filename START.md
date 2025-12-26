# Comment démarrer le jeu avec l'interface React

## Installation (à faire une seule fois)

### 1. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 2. Installer les dépendances React
```bash
cd database-ui
npm install
cd ..
```

## Démarrage (à faire à chaque fois)

Vous avez besoin de **3 terminaux** ouverts:

### Terminal 1: API Backend
```bash
python api.py
```
L'API démarre sur http://localhost:5000

### Terminal 2: Interface React
```bash
cd database-ui
npm start
```
L'interface React s'ouvre sur http://localhost:3000

### Terminal 3: Jeu
```bash
python game.py
```

## Comment jouer

1. **Lancez les 3 composants** (API, React, Jeu)
2. **Jouez au niveau 1** avec Pygame
3. **Trouvez le passage secret** (tout à droite, en haut)
4. **Appuyez sur →** dans le passage
5. **Votre navigateur s'ouvre** automatiquement sur l'interface React
6. **Gérez votre base de données** avec une vraie interface Google Drive!

## Fonctionnalités de l'interface React

- ✅ Vue dossiers style Google Drive
- ✅ Affichage des tables
- ✅ Créer des lignes (INSERT)
- ✅ Modifier des lignes (UPDATE)
- ✅ Supprimer des lignes (DELETE)
- ✅ Interface moderne et responsive
- ✅ Gestion d'erreurs

## Dépannage

**L'interface ne charge pas?**
- Vérifiez que l'API tourne (http://localhost:5000/api/tables)
- Vérifiez que React tourne (http://localhost:3000)

**CORS errors?**
- Flask-CORS est configuré pour accepter React

**Le jeu ne trouve pas le passage?**
- Allez tout à droite de l'écran
- Montez sur la plateforme en haut (x=1100)
- Continuez vers la droite jusqu'au bout
- Appuyez sur → (flèche droite)
