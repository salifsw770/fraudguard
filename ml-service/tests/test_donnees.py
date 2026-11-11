"""Tests de app/donnees.py, sur un petit CSV temporaire au format PaySim."""

import pandas as pd
import pytest

from app.donnees import COLONNES_TYPES, charger_paysim

EN_TETE = ",".join(COLONNES_TYPES) + "\n"
LIGNES = [
    "1,PAYMENT,9839.64,C1,170136.0,160296.36,M1,0.0,0.0,0,0\n",
    "1,TRANSFER,181.0,C2,181.0,0.0,C3,0.0,0.0,1,0\n",
    "2,CASH_OUT,181.0,C4,181.0,0.0,C5,21182.0,0.0,1,0\n",
    "3,CASH_IN,10000000.55,C6,0.0,10000000.55,C7,0.0,0.0,0,0\n",
]


def ecrire(tmp_path, contenu: str):
    chemin = tmp_path / "paysim.csv"
    chemin.write_text(contenu, encoding="utf-8", newline="")
    return chemin


@pytest.fixture
def csv_paysim(tmp_path):
    return ecrire(tmp_path, EN_TETE + "".join(LIGNES))


def test_charger_paysim_applique_les_types(csv_paysim):
    df = charger_paysim(csv_paysim)

    assert list(df.columns) == list(COLONNES_TYPES)
    assert df["step"].dtype == "int32"
    assert isinstance(df["type"].dtype, pd.CategoricalDtype)
    assert df["isFraud"].dtype == "int8"
    assert df["amount"].dtype == "float64"
    assert pd.api.types.is_string_dtype(df["nameOrig"])


def test_charger_paysim_garde_les_centimes_des_gros_montants(csv_paysim):
    df = charger_paysim(csv_paysim)

    assert df["amount"].iloc[3] == 10_000_000.55


def test_charger_paysim_sans_frac_renvoie_tout(csv_paysim):
    assert len(charger_paysim(csv_paysim)) == len(LIGNES)


def test_charger_paysim_echantillon_reproductible_et_ordonne(csv_paysim):
    premier = charger_paysim(csv_paysim, frac=0.5)
    second = charger_paysim(csv_paysim, frac=0.5)

    assert len(premier) == 2
    pd.testing.assert_frame_equal(premier, second)
    assert premier.index.is_monotonic_increasing


def test_charger_paysim_colonne_manquante_leve_une_erreur(tmp_path):
    chemin = ecrire(tmp_path, "step,type,amount\n1,PAYMENT,9839.64\n")

    with pytest.raises(ValueError, match="Colonnes manquantes.*nameOrig"):
        charger_paysim(chemin)
