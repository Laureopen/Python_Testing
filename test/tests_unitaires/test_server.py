import pytest
from server import app, clubs


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

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

