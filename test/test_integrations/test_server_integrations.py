import pytest
from server import app
from datetime import datetime, timedelta


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret'
    with app.test_client() as client:
        yield client


@pytest.fixture
def setup_club_and_competition(monkeypatch):
    # Crée 2 compétitions : une future, une passée
    now = datetime.now()
    future_date = (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
    past_date = (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

    club = {"name": "Test Club", "email": "test@club.com", "points": "10"}
    competitions = [
        {"name": "Future Competition", "numberOfPlaces": "10", "date": future_date},
        {"name": "Past Competition", "numberOfPlaces": "10", "date": past_date},
    ]

    monkeypatch.setattr("server.clubs", [club])
    monkeypatch.setattr("server.competitions", competitions)

    return club, competitions


def test_booking_scenarios(client, setup_club_and_competition):
    club, competitions = setup_club_and_competition
    club_name = club["name"]
    competition_future = competitions[0]["name"]
    competition_past = competitions[1]["name"]

    # 1. Réservation valide (3 places)
    resp = client.post('/purchasePlaces', data={
        "competition": competition_future,
        "club": club_name,
        "places": "3"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Great-booking complete!" in resp.data

    # 2. Réserver plus de 12 places → refusé
    resp = client.post('/purchasePlaces', data={
        "competition": competition_future,
        "club": club_name,
        "places": "13"
    }, follow_redirects=True)
    assert b"you can not book more than 12 places" in resp.data

    # 3. Réserver plus de points restants → refusé
    resp = client.post('/purchasePlaces', data={
        "competition": competition_future,
        "club": club_name,
        "places": "8"  # trop par rapport à points restants
    }, follow_redirects=True)
    assert b"you can not book more than available points" in resp.data

    # 4. Réserver pour une compétition passée → refusé
    resp = client.post('/purchasePlaces', data={
        "competition": competition_past,
        "club": club_name,
        "places": "1"
    }, follow_redirects=True)
    assert b"You cannot book place in past competition" in resp.data


def test_login_logout_and_invalid_email(client, setup_club_and_competition):
    club, _ = setup_club_and_competition

    # Login avec email invalide
    resp = client.post('/showSummary', data={'email': 'no@no.com'}, follow_redirects=True)
    assert b"cette adresse e-mail est introuvable." in resp.data

    # Simuler un login (session)
    with client.session_transaction() as session:
        session['club'] = club

    # Logout
    resp = client.get('/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b"Welcome" in resp.data or b"Login" in resp.data
