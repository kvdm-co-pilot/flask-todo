import pytest
from app import Todo, db, app

@pytest.fixture
def app_ctx():
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield

@pytest.fixture
def session(app_ctx):
    yield db.session

# create_todo_valid_title
def test_create_todo_valid_title(session):
    todo = Todo(title='Test', complete=False)
    session.add(todo)
    session.commit()
    assert todo.id is not None
    assert todo.title == 'Test'
    assert todo.complete is False

# create_todo_empty_title
def test_create_todo_empty_title(session):
    with pytest.raises(Exception):
        todo = Todo(title='', complete=False)
        session.add(todo)
        session.commit()

# create_todo_null_title
def test_create_todo_null_title(session):
    with pytest.raises(Exception):
        todo = Todo(title=None, complete=False)
        session.add(todo)
        session.commit()

# todo_id_autoincrement
def test_todo_id_autoincrement(session):
    t1 = Todo(title='A', complete=False)
    t2 = Todo(title='B', complete=False)
    session.add_all([t1, t2])
    session.commit()
    assert t2.id == t1.id + 1
