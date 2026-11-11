"""Vérifie la présence du dataset PaySim dans ml-service/data/raw/.

Ce script ne télécharge rien : PaySim se récupère manuellement sur Kaggle
(aucun identifiant Kaggle n'est nécessaire ni stocké dans le dépôt).
Il contrôle le fichier et son nombre de lignes, et n'affiche la marche à suivre
qu'en cas d'échec.

Usage :
    python download_data.py

Code de retour : 0 si le fichier est présent et complet, 1 sinon.
"""

import sys
from pathlib import Path

URL_KAGGLE = "https://www.kaggle.com/datasets/ealaxi/paysim1"
NOM_FICHIER = "PS_20174392719_1491204439457_log.csv"
DOSSIER_RAW = Path(__file__).resolve().parent / "data" / "raw"
CHEMIN_CSV = DOSSIER_RAW / NOM_FICHIER
NB_LIGNES_ATTENDU = 6_362_620  # lignes de données, en-tête exclu

INSTRUCTIONS = f"""\
Récupération manuelle de PaySim :
  1. Ouvrir {URL_KAGGLE} (compte Kaggle gratuit).
  2. Cliquer sur « Download » : on obtient une archive .zip.
  3. Extraire le CSV dans : {DOSSIER_RAW}
     sous le nom : {NOM_FICHIER}
     (si l'archive le nomme autrement, par exemple paysim.csv, le renommer).
  4. Relancer : python download_data.py
"""


def compter_lignes(chemin: str | Path) -> int:
    """Renvoie le nombre de lignes de données d'un CSV, en-tête exclu.

    Le fichier est lu en flux, ligne par ligne : la mémoire utilisée reste
    constante, même pour un fichier de plusieurs centaines de Mo.
    Une dernière ligne sans retour à la ligne final est bien comptée.
    """
    with open(chemin, "rb") as fichier:
        total = sum(1 for _ in fichier)
    return max(total - 1, 0)


def echec(message: str) -> int:
    """Affiche l'erreur suivie de la marche à suivre, et renvoie le code d'échec."""
    print(f"ÉCHEC : {message}\n", file=sys.stderr)
    print(INSTRUCTIONS, file=sys.stderr)
    return 1


def main(chemin: Path = CHEMIN_CSV) -> int:
    if not chemin.is_file():
        return echec(f"fichier introuvable : {chemin}")

    print(f"Fichier trouvé : {chemin}")
    print("Comptage des lignes (quelques secondes)...")
    nb_lignes = compter_lignes(chemin)

    if nb_lignes != NB_LIGNES_ATTENDU:
        return echec(
            f"{nb_lignes:,} lignes de données, {NB_LIGNES_ATTENDU:,} attendues. "
            "Le fichier est incomplet ou ce n'est pas PaySim : le télécharger à nouveau."
        )

    print(f"OK : {nb_lignes:,} lignes de données, le dataset PaySim est complet.")
    return 0


if __name__ == "__main__":
    # Sous Git Bash (Windows), la sortie serait encodée en cp1252 et les accents illisibles.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
