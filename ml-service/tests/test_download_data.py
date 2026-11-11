"""Tests de download_data.py, sans le vrai fichier PaySim.

Chaque test crée un petit CSV temporaire avec tmp_path (dossier unique par test,
supprimé automatiquement par pytest) : les tests sont rapides et tournent en CI.
"""

import download_data
from download_data import compter_lignes, main

EN_TETE = "step,type,amount,nameOrig,isFraud\n"


def ecrire(tmp_path, contenu: str, nom: str = "donnees.csv"):
    chemin = tmp_path / nom
    # newline="" : écrit les \n tels quels, même sous Windows.
    chemin.write_text(contenu, encoding="utf-8", newline="")
    return chemin


# --- compter_lignes ---------------------------------------------------------


def test_compter_lignes_ignore_l_en_tete(tmp_path):
    chemin = ecrire(tmp_path, EN_TETE + "1,PAYMENT,9839.64,C1,0\n2,TRANSFER,181.0,C2,1\n")

    assert compter_lignes(chemin) == 2


def test_compter_lignes_en_tete_seul_renvoie_zero(tmp_path):
    chemin = ecrire(tmp_path, EN_TETE)

    assert compter_lignes(chemin) == 0


def test_compter_lignes_fichier_vide_renvoie_zero(tmp_path):
    chemin = ecrire(tmp_path, "")

    assert compter_lignes(chemin) == 0


def test_compter_lignes_compte_la_derniere_ligne_sans_retour_final(tmp_path):
    chemin = ecrire(tmp_path, EN_TETE + "1,PAYMENT,9839.64,C1,0\n2,TRANSFER,181.0,C2,1")

    assert compter_lignes(chemin) == 2


def test_compter_lignes_accepte_un_chemin_texte(tmp_path):
    chemin = ecrire(tmp_path, EN_TETE + "1,PAYMENT,9839.64,C1,0\n")

    assert compter_lignes(str(chemin)) == 1


# --- main -------------------------------------------------------------------


def test_main_renvoie_1_si_fichier_absent(tmp_path):
    assert main(tmp_path / "absent.csv") == 1


def test_main_renvoie_1_si_nombre_de_lignes_incorrect(tmp_path):
    chemin = ecrire(tmp_path, EN_TETE + "1,PAYMENT,9839.64,C1,0\n")

    assert main(chemin) == 1


def test_main_renvoie_0_si_nombre_de_lignes_correct(tmp_path, monkeypatch):
    # On ne peut pas créer 6 362 620 lignes dans un test : on réduit la valeur attendue.
    monkeypatch.setattr(download_data, "NB_LIGNES_ATTENDU", 2)
    chemin = ecrire(tmp_path, EN_TETE + "1,PAYMENT,9839.64,C1,0\n2,TRANSFER,181.0,C2,1\n")

    assert main(chemin) == 0


def test_main_affiche_l_erreur_et_les_instructions_sur_stderr(tmp_path, capsys):
    main(tmp_path / "absent.csv")

    sortie = capsys.readouterr()
    assert "ÉCHEC : fichier introuvable" in sortie.err
    assert download_data.URL_KAGGLE in sortie.err
    assert sortie.out == ""
