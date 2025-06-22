import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_purchase_places_more_than_points(client, monkeypatch):
    #  Simuler un club avec seulement 2 points
    test_club = {"name": "Test Club", "email": "test@club.com", "points": "2"}
    test_competition = {"name": "Test Competition", "numberOfPlaces": "10", "date": "2025-12-12 10:00:00"}

    #  Patch les données dans server.py
    monkeypatch.setattr("server.clubs", [test_club])
    monkeypatch.setattr("server.competitions", [test_competition])

    #  Envoyer un formulaire avec 5 places (plus que les 2 points disponibles)
    response = client.post("/purchasePlaces", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "5"
    }, follow_redirects=True)

    #  Vérifier que le message d'erreur s'affiche
    assert b"you can not book more than available points" in response.data

def test_purchase_places_success(client, monkeypatch):
    test_club = {"name": "Test Club", "email": "test@club.com", "points": "10"}
    test_competition = {"name": "Test Competition", "numberOfPlaces": "15", "date": "2025-12-12 10:00:00"}

    monkeypatch.setattr("server.clubs", [test_club])
    monkeypatch.setattr("server.competitions", [test_competition])

    response = client.post("/purchasePlaces", data={
        "competition": "Test Competition",
        "club": "Test Club",
        "places": "3"
    }, follow_redirects=True)

    assert b"Great-booking complete!" in response.data
