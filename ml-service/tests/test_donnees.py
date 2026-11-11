"""Tests de app/donnees.py, sur un petit CSV temporaire au format PaySim."""

import pandas as pd
import pytest

from app.donnees import COLONNES_TYPES, charger_paysim, nettoyer

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


# --- nettoyer ---------------------------------------------------------------


def test_nettoyer_retire_is_flagged_fraud(csv_paysim):
    propre = nettoyer(charger_paysim(csv_paysim))

    assert "isFlaggedFraud" not in propre.columns
    assert len(propre.columns) == len(COLONNES_TYPES) - 1


def test_nettoyer_retire_les_doublons_exacts(tmp_path):
    chemin = ecrire(tmp_path, EN_TETE + LIGNES[0] + LIGNES[0] + LIGNES[1])

    assert len(nettoyer(charger_paysim(chemin))) == 2


def test_nettoyer_refuse_les_valeurs_manquantes(tmp_path):
    ligne_incomplete = "1,PAYMENT,,C1,170136.0,160296.36,M1,0.0,0.0,0,0\n"
    chemin = ecrire(tmp_path, EN_TETE + ligne_incomplete)

    with pytest.raises(ValueError, match=r"Valeurs manquantes : amount \(1\)"):
        nettoyer(charger_paysim(chemin))


def test_nettoyer_conserve_les_soldes_incoherents(csv_paysim):
    # Ligne 3 (CASH_OUT) : 21182 + 181 ≠ 0 côté destinataire. C'est un signal, pas une erreur.
    df = charger_paysim(csv_paysim)

    propre = nettoyer(df)

    colonnes_soldes = ["oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
    pd.testing.assert_frame_equal(propre[colonnes_soldes], df[colonnes_soldes])


def test_nettoyer_ne_modifie_pas_le_dataframe_recu(csv_paysim):
    df = charger_paysim(csv_paysim)
    copie = df.copy()

    nettoyer(df)

    pd.testing.assert_frame_equal(df, copie)


def test_parquet_conserve_les_types(csv_paysim, tmp_path):
    propre = nettoyer(charger_paysim(csv_paysim))
    chemin = tmp_path / "propre.parquet"

    propre.to_parquet(chemin)
    relu = pd.read_parquet(chemin)

    pd.testing.assert_frame_equal(relu, propre)
