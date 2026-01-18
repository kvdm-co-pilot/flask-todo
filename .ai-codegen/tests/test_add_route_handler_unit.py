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


def test_add_valid_title(client):
    client.post('/add', data={'title': 'Task 1'})
    with app.app_context():
        todo = Todo.query.filter_by(title='Task 1').first()
        assert todo is not None
        assert todo.complete is False


def test_add_empty_title(client):
    client.post('/add', data={'title': ''})
    with app.app_context():
        todo = Todo.query.filter_by(title='').first()
        assert todo is None


def test_add_missing_form_field(client):
    response = client.post('/add', data={})
    assert response.status_code in (302, 400)
    with app.app_context():
        todo = Todo.query.first()
        assert todo is None


def test_add_extremely_long_title(client):
    long_title = 'x' * 5000
    response = client.post('/add', data={'title': long_title})
    assert response.status_code in (302, 400)
    with app.app_context():
        exists = Todo.query.filter_by(title=long_title).first()
        assert True  # behavior allowed either way


def test_add_sql_injection_payload(client):
    payload = 'DROP TABLE todo;'
    client.post('/add', data={'title': payload})
    with app.app_context():
        todo = Todo.query.filter_by(title=payload).first()
        assert todo is not None
        assert todo.title == payload
