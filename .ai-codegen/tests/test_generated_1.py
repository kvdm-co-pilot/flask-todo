import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    ctx = app.app_context()
    ctx.push()
    db.drop_all()
    db.create_all()
    with app.test_client() as client:
        yield client
    ctx.pop()


def test_home_loads_successfully_returns_200(client):
    res = client.get('/')
    assert res.status_code == 200


def test_add_route_creates_todo_in_database(client):
    payload = {'title': 'Integration Task'}
    client.post('/add', data=payload)
    todos = Todo.query.all()
    assert len(todos) == 1
    assert todos[0].title == 'Integration Task'


def test_update_route_updates_todo(client):
    todo = Todo(title='Before', completed=False)
    db.session.add(todo)
    db.session.commit()
    client.post(f'/update/{todo.id}', data={'title': 'After', 'completed': 'on'})
    updated = Todo.query.get(todo.id)
    assert updated.title == 'After'
    assert updated.completed is True


def test_delete_route_removes_item(client):
    todo = Todo(title='Delete Me')
    db.session.add(todo)
    db.session.commit()
    client.get(f'/delete/{todo.id}')
    remaining = Todo.query.get(todo.id)
    assert remaining is None


def test_home_shows_created_todos(client):
    db.session.add(Todo(title='Visible'))
    db.session.commit()
    res = client.get('/')
    assert b'Visible' in res.data