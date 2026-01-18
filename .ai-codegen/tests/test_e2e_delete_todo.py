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

def test_bdd_delete_todo(client):
    with app.app_context():
        todo = Todo(title='Task', complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    response = client.get(f'/delete/{todo_id}', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Todo.query.filter_by(id=todo_id).first() is None
