import json
import server

def login(client, email="john@simplylift.co"):
    return client.post("/showSummary", data={"email": email}, follow_redirects=True)

def test_login_ok(client):
    rv = login(client)
    assert rv.status_code == 200
    assert b"Welcome" in rv.data  # texte présent dans welcome.html

def test_booking_happy_path_updates_points_and_places(client):
    # login
    rv = login(client)
    assert rv.status_code == 200

    # état avant
    club = next(c for c in server.clubs if c["email"] == "john@simplylift.co")
    comp = next(c for c in server.competitions if c["name"] == "Fall Classic")
    points_before = int(club["points"])
    places_before = int(comp["numberOfPlaces"])

    # achat de 3 places
    rv = client.post(
        "/purchasePlaces",
        data={"competition": "Fall Classic", "club": "Simply Lift", "places": "3"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    # message de succès (texte d’origine dans le POC)
    assert b"Great-booking complete!" in rv.data

    # état après
    assert int(club["points"]) == points_before - 3
    assert int(comp["numberOfPlaces"]) == places_before - 3

def test_booking_rejects_invalid_quantity(client):
    login(client)
    # 0 place → invalide
    rv = client.post(
        "/purchasePlaces",
        data={"competition": "Fall Classic", "club": "Simply Lift", "places": "0"},
        follow_redirects=True,
    )
    # on attend un message d’erreur flashé
    assert b"quantite" in rv.data.lower() or b"quantity" in rv.data.lower()
