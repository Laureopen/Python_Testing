import pytest
from server import app
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = "test"  # Nécessaire pour flash
    with app.test_client() as client:
        yield client

def test_booking_past_competition(client, monkeypatch):
    # Compétition passée (hier)
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    test_competition = {"name": "Past Competition", "numberOfPlaces": "10", "date": past_date}
    test_club = {"name": "Test Club", "email": "test@club.com", "points": "15"}

    monkeypatch.setattr("server.clubs", [test_club])
    monkeypatch.setattr("server.competitions", [test_competition])

    response = client.post("/purchasePlaces", data={
        "competition": "Past Competition",
        "club": "Test Club",
        "places": "2"
    }, follow_redirects=True)

    # Vérifie que le message d'erreur apparaît
    assert b"You cannot book place in past competition" in response.data

    # Vérifie que les places n'ont pas été modifiées
    assert test_competition["numberOfPlaces"] == "10"

    # Vérifie que les points du club n'ont pas changé
    assert test_club["points"] == "15"
