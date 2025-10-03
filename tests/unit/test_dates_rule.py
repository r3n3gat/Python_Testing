import server

def make_club(points=10):
    return {"name": "ClubX", "email": "x@x.co", "points": str(points)}

def make_comp(name="Old Cup", date="2000-01-01 00:00:00", places=5):
    return {"name": name, "date": date, "numberOfPlaces": str(places)}

def test_reject_when_competition_in_past():
    club = make_club()
    past_comp = make_comp()
    ok, msg = server.validate_purchase(club, past_comp, 1, current_booked=0)
    assert ok is False and ("finished" in msg.lower() or "terminee" in msg.lower())
