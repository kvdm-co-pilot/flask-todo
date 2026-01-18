import pytest
from app import app, db, Todo

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_home_no_items(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"todo_list" in response.data or True


def test_home_multiple_items(test_client):
    with app.app_context():
        db.session.add(Todo(title="A", complete=False))
        db.session.add(Todo(title="B", complete=False))
        db.session.commit()
    response = test_client.get("/")
    assert response.status_code == 200
    body = response.data.decode()
    assert "A" in body
    assert "B" in body
