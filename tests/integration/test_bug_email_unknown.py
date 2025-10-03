def test_unknown_email_shows_message(client):
    rv = client.post("/showSummary", data={"email": "unknown@example.com"}, follow_redirects=True)
    assert rv.status_code == 200
    assert b"adresse mail inconnue" in rv.data.lower()
