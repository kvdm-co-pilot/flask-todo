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

def test_bdd_update_todo(client):
    with app.app_context():
        todo = Todo(title='Test', complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id

    client.get(f'/update/{todo_id}')

    with app.app_context():
        updated = Todo.query.get(todo_id)
        assert updated.complete is True
