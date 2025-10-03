# tests/unit/test_rules.py
import server
import copy

def make_club(points=13, name="Simply Lift", email="john@simplylift.co"):
    return {"name": name, "email": email, "points": str(points)}

def make_comp(places=13, name="Fall Classic", date="2099-01-01 00:00:00"):
    return {"name": name, "date": date, "numberOfPlaces": str(places)}


def test_validate_purchase_happy_path():
    club = make_club(points=13)
    comp = make_comp(places=13)
    ok, msg = server.validate_purchase(club, comp, 3, current_booked=0)
    assert ok is True and msg is None

def test_reject_when_more_than_12():
    club = make_club(points=30)
    comp = make_comp(places=30)
    ok, msg = server.validate_purchase(club, comp, 13, current_booked=0)
    assert ok is False and "12" in msg

def test_reject_when_not_enough_places_left():
    club = make_club(points=30)
    comp = make_comp(places=2)
    ok, msg = server.validate_purchase(club, comp, 3, current_booked=0)
    assert ok is False and "places" in msg.lower()

def test_reject_when_not_enough_points():
    club = make_club(points=2)
    comp = make_comp(places=10)
    ok, msg = server.validate_purchase(club, comp, 3, current_booked=0)
    assert ok is False and "points" in msg.lower()

def test_cumulative_limit_12_per_club():
    club = make_club(points=30)
    comp = make_comp(places=30)
    # déjà 10 réservées pour ce club → il ne peut en prendre que 2 max
    ok, msg = server.validate_purchase(club, comp, 3, current_booked=10)
    assert ok is False and "12" in msg
