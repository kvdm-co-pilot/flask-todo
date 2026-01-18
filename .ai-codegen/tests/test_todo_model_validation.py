import pytest
from sqlalchemy.exc import IntegrityError
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


def test_create_valid_todo(test_client):
    with app.app_context():
        todo = Todo(title="Test Todo", complete=False)
        db.session.add(todo)
        db.session.commit()
        saved = Todo.query.first()
        assert saved is not None
        assert saved.title == "Test Todo"
        assert saved.complete is False


def test_create_empty_title_todo(test_client):
    with app.app_context():
        todo = Todo(title="", complete=False)
        db.session.add(todo)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_create_null_title_todo(test_client):
    with app.app_context():
        todo = Todo(title=None, complete=False)
        db.session.add(todo)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_toggle_complete_flag(test_client):
    with app.app_context():
        todo = Todo(title="Toggle", complete=False)
        db.session.add(todo)
        db.session.commit()
        todo.complete = not todo.complete
        db.session.commit()
        updated = Todo.query.first()
        assert updated.complete is True
