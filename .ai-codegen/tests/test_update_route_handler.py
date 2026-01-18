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


def test_update_existing_todo(test_client):
    with app.app_context():
        todo = Todo(title="Existing", complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    response = test_client.get(f"/update/{todo_id}")
    assert response.status_code == 302
    with app.app_context():
        updated = Todo.query.get(todo_id)
        assert updated.complete is True


def test_update_nonexistent_todo(test_client):
    response = test_client.get("/update/99999")
    assert response.status_code in (302, 404)


def test_update_invalid_id_format(test_client):
    response = test_client.get("/update/abc")
    assert response.status_code == 404
