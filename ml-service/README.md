# ml-service — service IA de FraudGuard

Exploration (notebooks), entraînement du modèle de détection de fraude (XGBoost + SHAP)
et API FastAPI `POST /predict`, appelée uniquement par le backend.

Données : **PaySim uniquement** (transactions simulées). Le dossier `data/` n'est jamais commité.

## 1. Prérequis

- **Python 3.12** : c'est la version de la CI et de l'image Docker. Une autre version
  (3.13, 3.14…) peut casser des paquets comme `xgboost`, `lightgbm` ou `shap`.
- Git.

Vérifier les versions disponibles :

```bash
py --list          # Windows : liste les Python installés
python3.12 --version   # Linux / macOS
```

## 2. Créer et activer l'environnement virtuel `.venv`

Toutes les commandes se lancent depuis `ml-service/`.

**Windows (Git Bash)**

```bash
cd ml-service
py -3.12 -m venv .venv
source .venv/Scripts/activate
python --version   # doit afficher Python 3.12.x
```

**Linux / macOS**

```bash
cd ml-service
python3.12 -m venv .venv
source .venv/bin/activate
python --version   # doit afficher Python 3.12.x
```

Pour quitter l'environnement : `deactivate`.

> Sans activation, on peut appeler directement l'interpréteur de l'environnement :
> `.venv/Scripts/python` (Windows) ou `.venv/bin/python` (Linux / macOS).

## 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

| Fichier | Contenu | Usage |
| --- | --- | --- |
| `requirements.txt` | pandas, numpy, pyarrow, scikit-learn, xgboost, lightgbm, shap, matplotlib, joblib, jupyter, ipykernel | exécution (image Docker) |
| `requirements-dev.txt` | `-r requirements.txt` + pytest, ruff, nbstripout | développement et CI |

Les versions sont figées (`==`) pour que tout le monde, la CI et Docker aient exactement
le même environnement. Dependabot propose chaque semaine les mises à jour par pull request.

## 4. Récupérer PaySim (manuellement)

Le dataset n'est pas téléchargé automatiquement et **aucun identifiant Kaggle n'est utilisé** :
pas d'API Kaggle, pas de `kaggle.json` dans le dépôt.

1. Ouvrir <https://www.kaggle.com/datasets/ealaxi/paysim1> (compte Kaggle gratuit).
2. Cliquer sur **Download** : on obtient une archive `.zip` (≈ 180 Mo).
3. Extraire le CSV (≈ 470 Mo) dans `ml-service/data/raw/` sous le nom
   `PS_20174392719_1491204439457_log.csv`. Si l'archive le nomme autrement
   (par exemple `paysim.csv`), le renommer.

```bash
mkdir -p data/raw
unzip -p ~/Downloads/archive.zip paysim.csv > data/raw/PS_20174392719_1491204439457_log.csv
```

## 5. Vérifier les données

```bash
python download_data.py
```

Le script rappelle la marche à suivre, puis vérifie que le fichier est présent et qu'il contient
**6 362 620 lignes de données** (en-tête exclu).

- Code de retour `0` : `OK : 6,362,620 lignes de données, le dataset PaySim est complet.`
- Code de retour `1` : fichier absent, ou nombre de lignes incorrect (téléchargement incomplet).

Vérifier aussi que Git ignore bien les données :

```bash
git status                       # data/ ne doit jamais apparaître
git check-ignore -v data/raw/PS_20174392719_1491204439457_log.csv
```

## 6. nbstripout : à relancer après chaque clone

`nbstripout` retire les sorties des notebooks (graphiques, tableaux, extraits de données)
**au moment du commit**. L'historique Git ne contient donc que le code des cellules : des diffs
lisibles, un dépôt léger, et aucune donnée qui fuit par une sortie.

Le fichier `.gitattributes` (commité) déclare le filtre pour `*.ipynb`, mais la commande
du filtre est enregistrée dans `.git/config`, qui **n'est pas versionné**. Après chaque clone
(ou si `.venv` est recréé), relancer depuis la **racine du dépôt**, `.venv` activé :

```bash
cd ..   # racine du dépôt
nbstripout --install --attributes .gitattributes
nbstripout --status   # doit afficher « nbstripout is installed »
```

Le fichier sur le disque garde ses sorties : seule la version enregistrée par Git est nettoyée.

## 7. Choisir le noyau `.venv` dans VS Code

Extensions nécessaires : **Python** et **Jupyter** (Microsoft).

1. Ouvrir le dossier du dépôt dans VS Code.
2. `Ctrl+Shift+P` → **Python: Select Interpreter** → choisir
   `ml-service/.venv/Scripts/python.exe` (Windows) ou `ml-service/.venv/bin/python` (Linux / macOS).
3. Dans un notebook : bouton **Select Kernel** en haut à droite → **Python Environments**
   → `.venv (Python 3.12.x)`.

Si `.venv` n'apparaît pas, vérifier que `ipykernel` est installé (il est dans `requirements.txt`)
puis recharger la fenêtre (`Ctrl+Shift+P` → **Developer: Reload Window**).

## 8. Commandes utiles

```bash
pytest                 # tests
ruff check .           # lint
ruff format .          # formatage
python download_data.py
```

## Organisation

```
ml-service/
  app/              code réutilisable et API FastAPI (testé)
  notebooks/        notebooks d'exploration numérotés (sorties retirées par nbstripout)
  models/           modèles entraînés
  tests/            tests pytest
  data/raw/         PaySim (non commité)
  download_data.py  vérification des données
```
