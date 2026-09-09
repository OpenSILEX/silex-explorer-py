"""
Tests documentant les bugs connus de `get_ls_exp`.

Chaque test décrit le comportement *attendu* et est marqué `xfail(strict=True)` :
tant que le bug existe, le test est XFAIL et la suite reste verte ; le jour où le
bug est corrigé, le test devient XPASS et fait échouer la suite, ce qui force à
retirer le marqueur. Aucun bug ne peut donc être corrigé puis oublié ici.

Le code source de `ls_exp.py` n'est volontairement pas modifié.
"""

import pandas as pd
import pytest

from silex_explorer_py.experiment.ls_exp import get_ls_exp
from silex_explorer_py.uri_name_manager import uri_name_table as uri_name_table_module

GRAPHQL_URL = "https://test.opensilex.org/graphql"


@pytest.fixture
def session():
    """Session d'authentification minimale, telle que produite par `login()`."""
    return {
        "url_graphql": GRAPHQL_URL,
        "headers_graphql": {
            "Authorization": "Bearer fake-token",
            "Content-Type": "application/json",
        },
    }


@pytest.fixture(autouse=True)
def _table_uri_name_isolee(monkeypatch):
    """Isole la table globale URI/Name que `get_ls_exp` mute en fin de parcours.

    `uri_name_table` n'existe pas au moment de l'import du module : elle n'est créée
    que par `init_uri_name()`. D'où `raising=False`, sans quoi le `setattr` échoue.
    monkeypatch supprime l'attribut après chaque test.
    """
    monkeypatch.setattr(
        uri_name_table_module,
        "uri_name_table",
        pd.DataFrame(columns=["URI", "Name"]),
        raising=False,
    )


@pytest.fixture(autouse=True)
def _cwd_temporaire(monkeypatch, tmp_path):
    """`get_ls_exp` peut écrire des CSV dans le répertoire courant : on l'y confine."""
    monkeypatch.chdir(tmp_path)


def graphql_ok(*experiments):
    """Enveloppe une liste d'expérimentations dans une réponse GraphQL valide."""
    return {"data": {"Experiment": list(experiments)}}


def experiment(
    _id="exp:1",
    label="Essai 1",
    start_date="2023-01-01",
    end_date="2023-12-31",
    species=("Arabidopsis thaliana",),
    projects=("Plant Research",),
):
    """Construit une expérimentation au format retourné par l'API GraphQL."""
    return {
        "_id": _id,
        "label": label,
        "startDate": start_date,
        "endDate": end_date,
        "hasSpecies": None if species is None else [{"label": s} for s in species],
        "hasProject": None if projects is None else [{"label": p} for p in projects],
    }


@pytest.mark.xfail(
    strict=True,
    reason=(
        "B1 : un resultat GraphQL vide produit un DataFrame sans colonnes ; "
        "tout filtre client leve alors KeyError (ls_exp.py:114 et :120) "
        "au lieu de retourner un DataFrame vide."
    ),
)
@pytest.mark.parametrize(
    "filtre",
    [
        pytest.param({"active_date": "2023-06-15"}, id="active_date"),
        pytest.param({"species_name": "Arabidopsis"}, id="species_name"),
        pytest.param({"project_name": "Plant Research"}, id="project_name"),
    ],
)
def test_resultat_vide_avec_filtre_client_retourne_df_vide(session, requests_mock, filtre):
    """Aucune expérimentation trouvée + un filtre client => DataFrame vide, pas d'erreur."""
    requests_mock.post(GRAPHQL_URL, json=graphql_ok())

    df = get_ls_exp(session, **filtre)

    assert isinstance(df, pd.DataFrame)
    assert df.empty


@pytest.mark.xfail(
    strict=True,
    reason=(
        "B2 : hasSpecies a null leve TypeError (ls_exp.py:101). "
        "Le defaut [] de .get() ne s'applique qu'a une cle absente, pas a une valeur None."
    ),
)
def test_species_null_donne_chaine_vide(session, requests_mock):
    """Un champ GraphQL nullable renvoye a null doit s'aplatir en chaine vide."""
    requests_mock.post(GRAPHQL_URL, json=graphql_ok(experiment(species=None)))

    df = get_ls_exp(session)

    assert df.loc[0, "hasSpecies"] == ""


@pytest.mark.xfail(
    strict=True,
    reason=(
        "B3 : str.contains est en regex=True par defaut (ls_exp.py:120), donc les "
        "parentheses d'un nom d'espece sont interpretees comme un groupe de capture "
        "et la ligne n'est jamais retenue. Correction : regex=False."
    ),
)
def test_species_name_avec_parentheses_matche_litteralement(session, requests_mock):
    """Un nom d'espece contenant des metacaracteres regex doit matcher litteralement."""
    nom_espece = "Zea mays (L.)"
    requests_mock.post(GRAPHQL_URL, json=graphql_ok(experiment(species=(nom_espece,))))

    df = get_ls_exp(session, species_name=nom_espece)

    assert len(df) == 1
    assert df.loc[0, "hasSpecies"] == nom_espece


@pytest.mark.xfail(
    strict=True,
    reason=(
        "B4 : endDate a null devient NaT, et la comparaison NaT >= date vaut False "
        "(ls_exp.py:116). Un essai demarre et sans date de fin est donc exclu alors "
        "qu'il est en cours."
    ),
)
def test_essai_sans_date_de_fin_est_actif(session, requests_mock):
    """Un essai demarre et sans endDate doit etre considere comme actif."""
    requests_mock.post(
        GRAPHQL_URL,
        json=graphql_ok(experiment(start_date="2023-01-01", end_date=None)),
    )

    df = get_ls_exp(session, active_date="2023-06-15")

    assert len(df) == 1
    assert df.loc[0, "URI"] == "exp:1"
