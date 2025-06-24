import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = "test"
    with app.test_client() as client:
        yield client

def test_booking_more_than_12_places(client, monkeypatch):
    test_club = {"name": "Test Club", "email": "test@club.com", "points": "50"}
    test_competition = {"name": "Test Competition", "numberOfPlaces": "25", "date": "2025-12-12 10:00:00"}

    monkeypatch.setattr("server.clubs", [test_club])
    monkeypatch.setattr("server.competitions", [test_competition])

    response = client.post("/purchasePlaces", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "13"  # > 12 → doit déclencher le bloc
    }, follow_redirects=True)

    # Vérifie que le message flash est bien là
    assert b"you can not book more than 12 places" in response.data

    # Vérifie que les données n'ont pas été modifiées
    assert test_competition["numberOfPlaces"] == "25"
    assert test_club["points"] == "50"
