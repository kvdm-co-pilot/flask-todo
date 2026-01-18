import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_bdd_add_todo(client):
    response = client.post('/add', data={'title': 'Test Todo'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Todo' in response.data
