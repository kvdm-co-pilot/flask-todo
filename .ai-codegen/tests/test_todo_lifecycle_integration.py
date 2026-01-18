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

def test_full_lifecycle(client):
    response = client.post('/add', data={'title': 'Task'})
    assert response.status_code == 302

    with app.app_context():
        todo = Todo.query.first()
        assert todo is not None
        todo_id = todo.id

    client.get(f'/update/{todo_id}')

    with app.app_context():
        updated = Todo.query.get(todo_id)
        assert updated.complete is True

    client.get(f'/delete/{todo_id}')

    with app.app_context():
        deleted = Todo.query.get(todo_id)
        assert deleted is None
