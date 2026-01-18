import pytest
from app import app, db, Todo

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

def test_boundary_title_len_0(client):
    response = client.post('/add', data={'title': ''}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Todo.query.count() == 0

def test_boundary_title_len_1(client):
    response = client.post('/add', data={'title': 'A'})
    assert response.status_code == 302
    with app.app_context():
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == 'A'

def test_boundary_title_len_max(client):
    title = 'X' * 255
    response = client.post('/add', data={'title': title})
    assert response.status_code in (302, 500)

def test_boundary_title_len_max_plus_one(client):
    title = 'X' * 256
    response = client.post('/add', data={'title': title})
    assert response.status_code in (400, 500)
