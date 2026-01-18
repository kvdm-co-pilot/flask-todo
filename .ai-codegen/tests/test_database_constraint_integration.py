import pytest
from app import app, db, Todo
from sqlalchemy.exc import IntegrityError

@pytest.fixture(autouse=True)
def setup_db():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    return app.test_client()

def test_insert_invalid_values(client):
    with pytest.raises(Exception):
        client.post('/add', data={'title': None})

def test_force_long_title(client):
    long_title = 'A' * 1000
    response = client.post('/add', data={'title': long_title})
    assert response.status_code in (302, 500)
