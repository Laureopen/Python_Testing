import pytest
from server import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Ajuster selon ton template


def test_show_summary_valid_email(client):
    response = client.post('/showSummary', data={'email': 'kate@shelifts.co.uk'})
    assert response.status_code == 200
    assert b"Competitions" in response.data or b"Booking" in response.data


def test_show_summary_invalid_email(client):
    response = client.post(
        '/showSummary',
        data={'email': 'invalid@example.com'},
        follow_redirects=True  # ← on suit la redirection automatiquement
    )
    assert response.status_code == 200
    assert b"cette adresse e-mail est introuvable." in response.data



import urllib.parse

def test_book_route(client):
    competition_name = urllib.parse.quote("Fall Classic")
    club_name = urllib.parse.quote("She Lifts")

    response = client.get(f'/book/{competition_name}/{club_name}')
    assert response.status_code == 200



def test_purchase_places(client):
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '1'
    })
    assert response.status_code == 200
    assert b"Great-booking complete!"in response.data or b"You cannot book place" in response.data