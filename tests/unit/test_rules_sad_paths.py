import server

def make_club(points=5):  # points faibles pour tests
    return {"name": "ClubX", "email": "x@x.co", "points": str(points)}

def make_comp(places=5):
    return {"name": "CompX", "date": "2099-01-01 00:00:00", "numberOfPlaces": str(places)}

def test_reject_non_integer_places():
    ok, msg = server.validate_purchase(make_club(), make_comp(), "abc", 0)
    assert ok is False and "quantity" in msg.lower()

def test_reject_zero_and_negative():
    ok0, msg0 = server.validate_purchase(make_club(), make_comp(), 0, 0)
    okm, msgm = server.validate_purchase(make_club(), make_comp(), -1, 0)
    assert ok0 is False and "quantity" in msg0.lower()
    assert okm is False and "quantity" in msgm.lower()

def test_reject_over_points_even_if_places_ok():
    ok, msg = server.validate_purchase(make_club(points=1), make_comp(places=10), 2, 0)
    assert ok is False and "points" in msg.lower()

def test_reject_over_competition_capacity():
    ok, msg = server.validate_purchase(make_club(points=10), make_comp(places=1), 2, 0)
    assert ok is False and "places" in msg.lower()

def test_reject_over_12_with_cumulative_bookings():
    ok, msg = server.validate_purchase(make_club(points=100), make_comp(places=100), 3, current_booked=11)
    assert ok is False and "12" in msg
