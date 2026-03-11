# TkImage Studio

**Application desktop de gestion, annotation et prétraitement d'images pour le Machine Learning.**

> Environnement local tout-en-un pour visualiser, transformer, annoter et exporter des images avant leur exploitation dans un pipeline ML.

|               |                        |
| ------------- | ---------------------- |
| **Version**   | 1.0.0                  |
| **Langage**   | Python 3               |
| **Encadrant** | Pr. Brahim BAKKAS      |
| **Stack**     | Tkinter · ttk · Pillow |
| **Date**      | Mars 2026              |

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Aperçu de l'interface](#aperçu-de-linterface)
- [Installation et lancement](#installation-et-lancement)
- [Guide d'utilisation](#guide-dutilisation)
- [Architecture du projet](#architecture-du-projet)
- [Système d'annotation](#système-dannotation)
- [Module IA](#module-ia)
- [Rapport de session](#rapport-de-session)
- [Raccourcis clavier](#raccourcis-clavier)
- [Choix techniques](#choix-techniques)
- [Perspectives](#perspectives)

---

## Fonctionnalités

### Visualisation

- Affichage d'images (PNG, JPG, BMP, GIF, TIFF)
- Zoom adaptatif et manuel (molette, `Ctrl+/−`, ajustement auto)
- Navigation dans un dossier (flèches, slider, explorateur de fichiers)
- Pan / déplacement par clic droit

### Traitement d'images

- **Transformations** : rotation 90°, redimensionnement, recadrage auto, recadrage souris, compression
- **12 filtres** : niveaux de gris, flou, netteté, contraste, luminosité, inversion, autocontraste, détection de contours, relief
- **Historique** : annuler / rétablir jusqu'à 15 niveaux, réinitialisation

### Annotation

- Labels / classes libres (créés par l'utilisateur)
- Statut, qualité, priorité, note (1-5)
- 12 attributs visuels en boutons toggle (Net, Flou, Complet, Tronqué…)
- Notes textuelles libres
- Persistance automatique par image

### Export

- Annotations en **JSON** ou **CSV**
- Rapport de session en **TXT** (journal d'actions avec statistiques)

### IA simulée

- Panneau de classification avec barre de confiance colorée
- Suggestion automatique de classe et description
- Architecture prête pour une connexion à une vraie API

---

## Aperçu de l'interface

```
┌──────────────────────────────────────────────────────────────────┐
│  Fichier │ Édition │ Vue │ Filtres │ Segmentation │ 3D │ Aide   │
├───────┬───┬───────────────────────────────────────┬───┬──────────┤
│       │   │                                       │   │          │
│ Barre │ E │                                       │   │ Panneau  │
│  d'   │ x │       Zone de visualisation           │   │  droit   │
│outils │ p │           (Canvas)                     │   │  IA &    │
│       │ l │                                       │   │Annotation│
│       │ o │                                       │   │          │
│       │ r │   ◀ Précédent  ═══════╪═══ Suivant ▶  │   │          │
├───────┴───┴───────────────────────────────────────┴───┴──────────┤
│  fichier.jpg                  1920×1080 · RGB             3/17   │
└──────────────────────────────────────────────────────────────────┘
```

L'interface est organisée en **4 zones** :

| Zone               | Description                                               |
| ------------------ | --------------------------------------------------------- |
| **Barre d'outils** | Accès rapide : fichier, édition, transformation, zoom     |
| **Explorateur**    | Arborescence des fichiers du dossier courant              |
| **Zone centrale**  | Canvas d'affichage avec zoom, pan et slider de navigation |
| **Panneau droit**  | Métadonnées, annotation, résultat IA, notes, rapport      |

Les panneaux latéraux sont **rétractables** (rail de 42 px) pour maximiser l'espace de visualisation.

Le thème est **clair et professionnel** : fond blanc, accent bleu `#4A6CF7`, contraste élevé.

---

## Installation et lancement

### Prérequis

- Python 3.8+
- Pillow

### Installation

```bash
pip install Pillow
```

### Lancement

```bash
cd tkimage_studio
python main.py
```

---

## Guide d'utilisation

### Workflow typique

1. **Ouvrir un dossier** d'images (`Ctrl+O` ou barre d'outils)
2. **Naviguer** entre les images (flèches `←` `→` ou slider)
3. **Annoter** : saisir un label, choisir statut/qualité/priorité/note, activer les tags
4. **Traiter** si nécessaire : appliquer filtres, rotation, recadrage
5. **Exporter** les annotations : Menu Fichier → Exporter annotations (JSON / CSV)
6. **Consulter le rapport** : Menu Fichier → Rapport de session

### Formats supportés

PNG, JPG, JPEG, BMP, GIF, TIF, TIFF

---

## Architecture du projet

```
tkimage_studio/
├── main.py                  # Point d'entrée et contrôleur
├── data/                    # Images de test (10 chats + 8 chiens)
└── src/
    ├── ui/                  # Interface utilisateur
    │   ├── main_window.py       Fenêtre principale (layout grille)
    │   ├── menu_bar.py          Barre de menus
    │   ├── left_toolbar.py      Barre d'outils gauche
    │   ├── image_viewer.py      Visualiseur central (canvas + zoom)
    │   ├── right_panel.py       Panneau droit (annotation + IA)
    │   ├── status_panel.py      Barre de statut
    │   ├── file_explorer.py     Explorateur de fichiers (Treeview)
    │   └── theme.py             Thème ttk personnalisé
    ├── core/                # Logique métier
    │   ├── image_processor.py   Traitement d'images (filtres, undo/redo)
    │   ├── file_manager.py      Gestion de fichiers et navigation
    │   └── activity_logger.py   Journalisation des actions
    └── utils/
        └── constants.py         Couleurs, polices, catégories
```

### Organisation MVC

| Couche         | Modules   | Rôle                        |
| -------------- | --------- | --------------------------- |
| **Modèle**     | `core/`   | Données et logique métier   |
| **Vue**        | `ui/`     | Affichage et interaction    |
| **Contrôleur** | `main.py` | Orchestration via callbacks |

Le contrôleur expose un **dictionnaire de 65 callbacks** transmis aux widgets UI, assurant un découplage total entre les couches.

---

## Système d'annotation

Le système est **indépendant du domaine** — il fonctionne avec tout type d'images (médical, industriel, faune, etc.).

### Champs disponibles

| Champ          | Type              | Valeurs possibles                                        |
| -------------- | ----------------- | -------------------------------------------------------- |
| Label / Classe | Texte libre       | Défini par l'utilisateur                                 |
| Statut         | Liste             | Non annoté, En cours, Annoté, À vérifier, Validé, Rejeté |
| Qualité        | Liste             | Excellente, Bonne, Acceptable, Médiocre, Inutilisable    |
| Priorité       | Liste             | Basse, Normale, Haute, Urgente                           |
| Note           | 1 à 5             | Notation de l'image                                      |
| Attributs      | 12 boutons toggle | Net, Flou, Surexposé, Sous-exposé, Bruité, Complet, etc. |
| Notes          | Texte libre       | Description manuelle                                     |

### Export

**JSON** — structure clé/valeur par image :

```json
{
  "Cat 1.JPG": {
    "label": "Chat",
    "status": "Annoté",
    "quality": "Bonne",
    "note": "4",
    "tags": ["Net", "Complet"]
  }
}
```

**CSV** — une ligne par image :

```
fichier,label,statut,qualite,priorite,note,tags,notes
Cat 1.JPG,Chat,Annoté,Bonne,Normale,4,Net;Complet,Image nette
```

---

## Module IA

Le panneau IA intègre une **simulation de classification** (ResNet-50) :

- **Analyse** : suggestion de classe avec indice de confiance (barre colorée)
- **Description** : génération automatique de description textuelle
- **Intégration** : la classe suggérée est ajoutée aux labels, le statut passe à « À vérifier »

> L'architecture est prête pour une connexion à une vraie API (OpenAI Vision, Hugging Face, modèle local). Il suffit de remplacer le contenu de `run_ia_analysis()`.

---

## Rapport de session

Le module `ActivityLogger` enregistre chaque action avec horodatage et catégorie.

Le rapport affiche :

- Durée de session et nombre total d'actions
- Statistiques par catégorie (barres graphiques)
- Journal détaillé chronologique

Export en `.txt` :

```
╔══════════════════════════════════════════════╗
║      RAPPORT DE SESSION – TkImage Studio     ║
╠══════════════════════════════════════════════╣
║  Début   : 09/03/2026 14:30:00              ║
║  Durée   : 0h 25m 30s                       ║
║  Actions : 42                                ║
╚══════════════════════════════════════════════╝

 fichier  ████████████████░░░░░  18
 filtre   ██████████░░░░░░░░░░░  10
 outil    ██████░░░░░░░░░░░░░░░   6
```

---

## Raccourcis clavier

| Raccourci            | Action                      |
| -------------------- | --------------------------- |
| `Ctrl+O`             | Ouvrir une image            |
| `Ctrl+S`             | Enregistrer                 |
| `Ctrl+Shift+S`       | Enregistrer sous            |
| `Ctrl+Z`             | Annuler                     |
| `Ctrl+Y`             | Rétablir                    |
| `Ctrl+R`             | Réinitialiser l'image       |
| `←` / `→`            | Image précédente / suivante |
| `Ctrl+` / `Ctrl-`    | Zoom avant / arrière        |
| `Ctrl+0`             | Ajuster à la fenêtre        |
| Molette              | Zoom                        |
| Clic droit + glisser | Déplacer l'image (pan)      |

---

## Choix techniques

| Aspect                | Choix                                                                |
| --------------------- | -------------------------------------------------------------------- |
| **Pattern principal** | Dictionnaire de callbacks — découplage UI / métier                   |
| **Undo/Redo**         | Double pile (history + redo_stack), 15 niveaux max                   |
| **Resampling**        | LANCZOS pour toutes les opérations de redimensionnement              |
| **Thème**             | ttk `clam` personnalisé — 20+ styles (frames, labels, boutons, etc.) |
| **Scroll**            | Binding récursif du mousewheel sur tous les widgets enfants          |

---

## Perspectives

| Version | Évolution envisagée                                              |
| ------- | ---------------------------------------------------------------- |
| v1.1    | Connexion à une vraie API IA (OpenAI Vision, Hugging Face)       |
| v1.2    | Segmentation réelle (seuillage Otsu, masques binaires via NumPy) |
| v1.3    | Visualisation 3D (matplotlib, empilements DICOM)                 |
| v2.0    | Système de plugins, clé API configurable, prompts personnalisés  |

---

_TkImage Studio — Mars 2026_
