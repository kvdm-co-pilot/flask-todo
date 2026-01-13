import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client


def test_home_loads_successfully_returns_200(client):
    # Arrange

    # Act
    res = client.get('/')

    # Assert
    assert res.status_code == 200


def test_add_route_creates_todo_in_database(client):
    # Arrange
    payload = {'title': 'Integration Task'}

    # Act
    client.post('/add', data=payload)
    todos = Todo.query.all()

    # Assert
    assert len(todos) == 1
    assert todos[0].title == 'Integration Task'


def test_update_route_updates_todo(client):
    # Arrange
    todo = Todo(title='Before', completed=False)
    db.session.add(todo)
    db.session.commit()

    # Act
    client.post(f'/update/{todo.id}', data={'title': 'After', 'completed': 'on'})
    updated = Todo.query.get(todo.id)

    # Assert
    assert updated.title == 'After'
    assert updated.completed is True


def test_delete_route_removes_item(client):
    # Arrange
    todo = Todo(title='Delete Me')
    db.session.add(todo)
    db.session.commit()

    # Act
    client.get(f'/delete/{todo.id}')
    remaining = Todo.query.get(todo.id)

    # Assert
    assert remaining is None


def test_home_shows_created_todos(client):
    # Arrange
    db.session.add(Todo(title='Visible'))
    db.session.commit()

    # Act
    res = client.get('/')

    # Assert
    assert b'Visible' in res.data