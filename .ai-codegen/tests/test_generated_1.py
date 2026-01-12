from flask import g
import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        with app.test_client() as client:
            yield client

def test_home_loads_successfully_returns_200(client):
    res = client.get('/')
    assert res.status_code == 200

def test_add_route_creates_todo_in_database(client):
    payload = {'title': 'Integration Task'}
    client.post('/add', data=payload)
    with app.app_context():
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == 'Integration Task'

def test_update_route_updates_todo(client):
    with app.app_context():
        todo = Todo(title='Before', complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    client.post(f'/update/{todo_id}', data={'title': 'After', 'complete': 'on'})
    with app.app_context():
        updated = Todo.query.get(todo_id)
        assert updated.title == 'After'
        assert updated.complete is True

def test_delete_route_removes_item(client):
    with app.app_context():
        todo = Todo(title='Delete Me', complete=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    client.get(f'/delete/{todo_id}')
    with app.app_context():
        remaining = Todo.query.get(todo_id)
        assert remaining is None

def test_home_shows_created_todos(client):
    with app.app_context():
        db.session.add(Todo(title='Visible', complete=False))
        db.session.commit()
    res = client.get('/')
    assert b'Visible' in res.data