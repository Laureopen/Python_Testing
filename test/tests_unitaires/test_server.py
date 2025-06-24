import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_competition_places_are_decreased(client, monkeypatch):
    # Club avec assez de points
    test_club = {"name": "Test Club", "email": "test@club.com", "points": "20"}
    # Compétition avec 10 places
    test_competition = {"name": "Test Competition", "numberOfPlaces": "10", "date": "2025-12-12 10:00:00"}

    # Patch les données directement dans server.py
    monkeypatch.setattr("server.clubs", [test_club])
    monkeypatch.setattr("server.competitions", [test_competition])

    # POST de réservation de 3 places
    response = client.post("/purchasePlaces", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "3"
    }, follow_redirects=True)

    #  Vérifie que la compétition a bien été mise à jour
    assert test_competition["numberOfPlaces"] == 7  # 10 - 3

