"""Chargement du dataset PaySim, partagé par les notebooks et le service IA.

Les types des colonnes sont fixés à la lecture : pandas n'a pas à les deviner,
la mémoire est réduite et tous les notebooks voient exactement les mêmes données.
"""

from pathlib import Path

import pandas as pd

DOSSIER_DATA = Path(__file__).resolve().parent.parent / "data"
CHEMIN_CSV_PAYSIM = DOSSIER_DATA / "raw" / "PS_20174392719_1491204439457_log.csv"
DOSSIER_PROCESSED = DOSSIER_DATA / "processed"
CHEMIN_PARQUET = DOSSIER_PROCESSED / "paysim_propre.parquet"

# Montants et soldes en float64, pas float32 : le float32 n'a qu'environ 7 chiffres
# significatifs, les centimes des gros montants seraient perdus et créeraient de fausses
# incohérences de soldes.
COLONNES_TYPES = {
    "step": "int32",  # heure de la simulation (1 à 743) : sert au découpage dans le temps
    "type": "category",  # 5 valeurs seulement : PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN
    "amount": "float64",
    "nameOrig": "str",
    "oldbalanceOrg": "float64",
    "newbalanceOrig": "float64",
    "nameDest": "str",
    "oldbalanceDest": "float64",
    "newbalanceDest": "float64",
    "isFraud": "int8",
    "isFlaggedFraud": "int8",
}


def charger_paysim(
    chemin: str | Path = CHEMIN_CSV_PAYSIM,
    frac: float | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Lit le CSV PaySim avec des types fixés, et renvoie éventuellement un échantillon.

    frac : part des lignes à garder (ex. 0.1 pour 10 %) ; None renvoie tout le fichier.
    L'échantillon est reproductible (random_state) et remis dans l'ordre d'origine,
    c'est-à-dire l'ordre chronologique des transactions.

    Lève ValueError si une colonne attendue manque, avant de lire tout le fichier.
    """
    # nrows=0 : on lit seulement l'en-tête, pour échouer vite sur un mauvais fichier.
    colonnes = pd.read_csv(chemin, nrows=0).columns
    manquantes = [nom for nom in COLONNES_TYPES if nom not in colonnes]
    if manquantes:
        raise ValueError(f"Colonnes manquantes dans {chemin} : {', '.join(manquantes)}")

    df = pd.read_csv(chemin, usecols=list(COLONNES_TYPES), dtype=COLONNES_TYPES)

    if frac is not None:
        df = df.sample(frac=frac, random_state=random_state).sort_index()
    return df


def nettoyer(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage minimal de PaySim, décidé à partir du notebook 01_exploration.

    - Refuse les valeurs manquantes (ValueError) plutôt que de les combler en silence.
    - Retire isFlaggedFraud : c'est la sortie d'une règle existante, pas une donnée de la
      transaction ; une transaction reçue par l'API ne l'aura pas.
    - Retire les doublons exacts.

    Tout le reste est conservé volontairement : les soldes incohérents sont un signal de
    fraude (à ne pas « corriger »), et le choix des types et des variables se fait au notebook 02.
    Renvoie un nouveau DataFrame ; celui reçu n'est pas modifié.
    """
    manquantes = df.isna().sum()
    if manquantes.any():
        detail = ", ".join(f"{nom} ({n})" for nom, n in manquantes[manquantes > 0].items())
        raise ValueError(f"Valeurs manquantes : {detail}")

    return df.drop(columns="isFlaggedFraud").drop_duplicates()
