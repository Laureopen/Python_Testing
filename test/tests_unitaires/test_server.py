import pytest
from server import app, clubs
from datetime import datetime, timedelta


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = "test"
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

def test_showSummary_email_found(client):
    test_email = "test@example.com"
    test_club = {'email': test_email, 'name': 'Test Club'}
    clubs.append(test_club)

    response = client.post('/showSummary', data={'email': test_email})
    assert response.status_code == 200

    html = response.data.decode('utf-8')
    assert 'Test%20Club' in html  # ou '/book/Test%20Club'

    clubs.remove(test_club)

def test_showSummary_email_not_found(client):
    response = client.post('/showSummary', data={'email': 'inexistant@example.com'}, follow_redirects=True)
    assert response.status_code == 200

    html = response.data.decode('utf-8')
    assert "Désolé, cette adresse e-mail est introuvable." in html

def test_display_clubs_points(client, monkeypatch):
    test_clubs = [
        {"name": "Club Alpha", "email": "alpha@club.com", "points": "20"},
        {"name": "Club Beta", "email": "beta@club.com", "points": "15"}
    ]

    # Patch les données clubs dans le module server
    monkeypatch.setattr("server.clubs", test_clubs)

    # Appel GET de la route
    response = client.get('/clubsPoints')

    assert response.status_code == 200
    html = response.data.decode()

    # Vérifie que les noms et points sont affichés dans la page
    assert "Club Alpha" in html
    assert "20" in html
    assert "Club Beta" in html
    assert "15" in html




