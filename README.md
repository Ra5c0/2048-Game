# 🎮 2048 – Pygame (ZQSD Edition)

Un clone moderne du célèbre **jeu 2048**, développé en **Python + Pygame**, avec :

- 🎨 **Thème clair / sombre** (touche `C`)
- 🧩 **Choix de la taille de grille** (4×4, 5×5 ou 6×6)
- 🎞️ **Animations fluides** (glissement, fusion, pop)
- 🧠 **Contrôles ZQSD et flèches**
- 💾 **Sauvegarde automatique** du meilleur score et du thème

---

## 🧰 Installation

1. **Cloner le projet ou télécharger le fichier :**
   ```
   git clone https://github.com/<ton-repo>/2048-pygame.git
   cd 2048-pygame
   ```


2. **Installer la dépendance :**
    ```
    pip install pygame
    ```

3. **Lancer le jeu :**
    ```
    python 2048_modern.py
    ```

## 🎮 Contrôles

| Action                      | Touche(s)  |
| :-------------------------- | :--------- |
| Déplacer vers le haut       | `Z` ou `↑` |
| Déplacer vers la gauche     | `Q` ou `←` |
| Déplacer vers le bas        | `S` ou `↓` |
| Déplacer vers la droite     | `D` ou `→` |
| Rejouer (retour menu)       | `R`        |
| Basculer thème clair/sombre | `C`        |
| Quitter le jeu              | `Échap`    |

## 🕹️ Fonctionnalités

### 🧩 Menu de démarrage

- Choix entre une grille 4×4, 5×5 ou 6×6
- Affichage cohérent selon le thème sélectionné

### 🎨 Interface fluide et moderne

- Animations de glissement, fusion et apparition
- Interface responsive (fenêtre redimensionnable)
- Design sobre et élégant

### 💾 Persistance automatique

- Sauvegarde du meilleur score pour chaque taille de grille
- Sauvegarde du thème préféré (clair ou sombre) → stockées dans 2048_prefs.json

### ⚙️ Optimisations

- Aucune apparition prématurée de tuiles (l’animation suit la logique du jeu)
- Aucune dépendance autre que Pygame

## 📁 Structure du projet

    .
    ├── 2048_modern.py       # Code principal du jeu
    ├── 2048_prefs.json      # Fichier de préférences (thème + scores)
    ├── README.md            # Ce fichier
    └── requirements.txt     # Librairie
