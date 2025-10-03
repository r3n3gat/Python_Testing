import server
import pytest

def test_competition_in_past_invalid_date():
    assert server.competition_in_past({"date": "???"}) is False

def test_logout_clears_session(client):
    # login
    resp = client.post("/showSummary", data={"email": "john@simplylift.co"}, follow_redirects=True)
    assert resp.status_code == 200
    # logout
    resp = client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    # tente un achat -> doit rediriger avec "Données invalides"
    resp = client.post("/purchasePlaces",
                       data={"competition": "Fall Classic", "places": "1"},
                       follow_redirects=True)
    assert b"Donn" in resp.data  # message générique, selon ta version exacte

def test_purchase_guard_negative_paths(monkeypatch, client):
    # force validate_purchase à renvoyer OK pour passer la garde locale
    monkeypatch.setattr(server, "validate_purchase", lambda *a, **k: (True, None))
    # login
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    # place la compet avec 0 places, et le club avec 0 points pour déclencher le garde-fou
    comp = server.find_comp_by_name("Fall Classic")
    club = server.find_club_by_name("Simply Lift")
    comp["numberOfPlaces"] = "0"
    club["points"] = "0"
    resp = client.post("/purchasePlaces",
                       data={"competition": "Fall Classic", "places": "1"},
                       follow_redirects=True)
    assert b"Erreur de calcul des points/places" in resp.data