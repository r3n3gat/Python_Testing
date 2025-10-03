# tests/conftest.py
import sys
from pathlib import Path

# Assure que le répertoire racine (celui qui contient server.py) est dans sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
import copy
import json
import server


@pytest.fixture
def client():
    """
    Client de test Flask + remise à zéro des données entre tests.
    """
    server.app.config.update(TESTING=True, SECRET_KEY="test")

    # recharge les données depuis les fichiers JSON à chaque test
    with open("clubs.json", "r", encoding="utf-8") as f:
        clubs = json.load(f)["clubs"]
    with open("competitions.json", "r", encoding="utf-8") as f:
        competitions = json.load(f)["competitions"]

    # Forcer "Fall Classic" dans le futur pour les scénarios "happy path"
    for comp in competitions:
        if comp.get("name") == "Fall Classic":
            comp["date"] = "2099-01-01 00:00:00"

    server.clubs = copy.deepcopy(clubs)
    server.competitions = copy.deepcopy(competitions)

    # si on ajoute un suivi des réservations par club, on le remet à zéro
    if hasattr(server, "club_bookings"):
        server.club_bookings = {}

    with server.app.test_client() as c:
        yield c
