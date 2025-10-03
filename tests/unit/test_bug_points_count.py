import server

def test_points_decrease_exactly():
    club = {"name": "C", "email": "c@c.co", "points": "6"}
    comp = {"name": "X", "date": "2099-01-01 00:00:00", "numberOfPlaces": "10"}
    ok, msg = server.validate_purchase(club, comp, 4, current_booked=0)
    assert ok is True
    # simule l’application
    comp["numberOfPlaces"] = str(int(comp["numberOfPlaces"]) - 4)
    club["points"] = str(int(club["points"]) - 4)
    assert comp["numberOfPlaces"] == "6"
    assert club["points"] == "2"
