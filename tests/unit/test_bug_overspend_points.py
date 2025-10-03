import server

def test_cannot_spend_more_points_than_owned():
    club = {"name": "C", "email": "c@c.co", "points": "2"}
    comp = {"name": "X", "date": "2099-01-01 00:00:00", "numberOfPlaces": "10"}
    ok, msg = server.validate_purchase(club, comp, 3, current_booked=0)
    assert ok is False and "points" in msg.lower()
