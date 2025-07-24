import pytest
from server import app, clubs, competitions
from datetime import datetime, timedelta


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret'
    with app.test_client() as client:
        yield client


@pytest.fixture
def setup_data(monkeypatch):
    # Setup initial state : un club et une compétition dans le futur
    initial_points = 10
    initial_places = 10
    test_club = {"name": "Integration Club", "email": "integration@club.com", "points": str(initial_points)}
    future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    test_competition = {"name": "Integration Competition", "numberOfPlaces": str(initial_places), "date": future_date}

    monkeypatch.setattr("server.clubs", [test_club])
    monkeypatch.setattr("server.competitions", [test_competition])

    return test_club, test_competition, initial_points, initial_places


@pytest.fixture
def setup_data_past(monkeypatch):
    # Setup initial state : un club et une compétition dans le passé
    initial_points = 10
    initial_places = 10
    test_club = {"name": "Past Club", "email": "past@club.com", "points": str(initial_points)}
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    test_competition = {"name": "Past Competition", "numberOfPlaces": str(initial_places), "date": past_date}

    monkeypatch.setattr("server.clubs", [test_club])
    monkeypatch.setattr("server.competitions", [test_competition])

    return test_club, test_competition, initial_points, initial_places


def test_reserve_3_places_success(client, setup_data):
    test_club, test_competition, initial_points, initial_places = setup_data

    response = client.post('/purchasePlaces', data={
        "competition": test_competition["name"],
        "club": test_club["name"],
        "places": "3"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data

    assert int(test_competition["numberOfPlaces"]) == initial_places - 3
    assert int(test_club["points"]) == initial_points - 3


def test_reserve_more_than_12_places_fails(client, setup_data):
    test_club, test_competition, _, _ = setup_data

    response = client.post('/purchasePlaces', data={
        "competition": test_competition["name"],
        "club": test_club["name"],
        "places": "13"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"you can not book more than 12 places" in response.data


def test_reserve_2_places_success(client, setup_data):
    test_club, test_competition, initial_points, initial_places = setup_data

    # Première réservation de 3 places (pour avancer le scénario)
    client.post('/purchasePlaces', data={
        "competition": test_competition["name"],
        "club": test_club["name"],
        "places": "3"
    }, follow_redirects=True)

    # Puis réservation de 2 places
    response = client.post('/purchasePlaces', data={
        "competition": test_competition["name"],
        "club": test_club["name"],
        "places": "2"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data

    assert int(test_competition["numberOfPlaces"]) == initial_places - 5
    assert int(test_club["points"]) == initial_points - 5


def test_reserve_more_places_than_points_fails(client, setup_data):
    test_club, test_competition, initial_points, initial_places = setup_data

    # Première réservation de 5 places (pour avancer le scénario)
    client.post('/purchasePlaces', data={
        "competition": test_competition["name"],
        "club": test_club["name"],
        "places": "5"
    }, follow_redirects=True)

    # Essayer de réserver 6 places (plus que les points restants)
    response = client.post('/purchasePlaces', data={
        "competition": test_competition["name"],
        "club": test_club["name"],
        "places": "6"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"you can not book more than available points" in response.data


def test_reservation_on_past_competition_fails(client, setup_data_past):
    test_club, test_competition, _, _ = setup_data_past

    response = client.post('/purchasePlaces', data={
        "competition": test_competition["name"],
        "club": test_club["name"],
        "places": "1"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"You cannot book place in past competition" in response.data


def test_logout(client, setup_data):
    test_club, _, _, _ = setup_data

    # Simuler une session active
    with client.session_transaction() as sess:
        sess['club'] = test_club

    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Login" in response.data


def test_show_summary_with_invalid_email(client):
    invalid_email = "no-such-email@example.com"

    response = client.post('/showSummary', data={'email': invalid_email}, follow_redirects=True)

    assert response.status_code == 200
    assert b"cette adresse e-mail est introuvable." in response.data
