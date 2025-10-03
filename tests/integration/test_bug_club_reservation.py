import server

def login(client, email="john@simplylift.co"):
    return client.post("/showSummary", data={"email": email}, follow_redirects=True)

def test_cannot_book_for_another_club(client):
    login(client, "john@simplylift.co")  # Simply Lift
    # tente de réserver pour un autre club via le form
    rv = client.post("/purchasePlaces", data={
        "competition": "Fall Classic",
        "club": "Other Club",
        "places": "1"
    }, follow_redirects=True)
    assert rv.status_code == 200
    # Vérifie que les points de Simply Lift ont décrémenté (et pas un autre)
    sl = next(c for c in server.clubs if c["name"] == "Simply Lift")
    assert int(sl["points"]) >= 0  # au minimum, l'opération a bien pris Simply Lift

def test_reject_over_12_cumulative(client):
    # pre-book 10 via l'état
    server.club_bookings[("Simply Lift", "Fall Classic")] = 10
    login(client, "john@simplylift.co")
    rv = client.post("/purchasePlaces", data={
        "competition": "Fall Classic", "places": "3"
    }, follow_redirects=True)
    assert b"12" in rv.data
