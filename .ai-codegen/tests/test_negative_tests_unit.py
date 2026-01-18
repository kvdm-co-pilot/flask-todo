import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            t = Todo(title='Sample', complete=False)
            db.session.add(t)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


def test_negative_update_using_post(client):
    with app.app_context():
        todo = Todo.query.first()
    response = client.post(f'/update/{todo.id}')
    assert response.status_code == 405


def test_negative_add_invalid_mime_type(client):
    response = client.post('/add', data='invalid', content_type='application/json')
    assert response.status_code in (400, 415, 500)
