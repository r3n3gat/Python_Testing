import server

def login(client, email="john@simplylift.co"):
    return client.post("/showSummary", data={"email": email}, follow_redirects=True)

def test_booking_is_blocked_if_competition_is_past(client):
    # La fixture a mis Fall Classic dans le futur. On force ici le passé pour CE test.
    for comp in server.competitions:
        if comp["name"] == "Fall Classic":
            comp["date"] = "2000-01-01 00:00:00"

    login(client)
    rv = client.post(
        "/purchasePlaces",
        data={"competition": "Fall Classic", "club": "Simply Lift", "places": "1"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert b"finished" in rv.data.lower() or b"terminee" in rv.data.lower()
