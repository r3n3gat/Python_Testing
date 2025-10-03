import server

def login(client, email="john@simplylift.co"):
    return client.post("/showSummary", data={"email": email}, follow_redirects=True)

def test_login_unknown_email(client):
    rv = client.post("/showSummary", data={"email": "unknown@example.com"}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"Email inconnu" in rv.data

def test_purchase_with_missing_form_fields(client):
    login(client)
    # pas de 'places' -> devrait être traité comme invalide
    rv = client.post("/purchasePlaces", data={"competition": "Fall Classic", "club": "Simply Lift"}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"quantity" in rv.data.lower()

def test_purchase_with_invalid_comp_or_club(client):
    login(client)
    rv = client.post("/purchasePlaces", data={"competition": "Nope", "club": "Simply Lift", "places": "1"}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"invalides" in rv.data.lower() or b"invalid" in rv.data.lower()
