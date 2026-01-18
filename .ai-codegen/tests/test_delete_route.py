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

def test_delete_existing_todo(client):
    with app.app_context():
        todo = Todo(title='DeleteMe', complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    response = client.get(f'/delete/{todo_id}')
    assert response.status_code == 302
    with app.app_context():
        assert Todo.query.filter_by(id=todo_id).first() is None

def test_delete_nonexistent_todo(client):
    response = client.get('/delete/99999')
    assert response.status_code in (302, 404, 500)

def test_delete_invalid_id_format(client):
    response = client.get('/delete/xyz')
    assert response.status_code in (404, 400)
