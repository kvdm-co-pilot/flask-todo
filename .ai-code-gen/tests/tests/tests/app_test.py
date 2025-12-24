from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Todo
import pytest


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    # Flask-SQLAlchemy models do not expose Base.metadata; create table directly
    Todo.__table__.create(engine)
    Session = sessionmaker(bind=engine)
    return Session()


# Unique test suite name derived from full entity path: app.Todo
class App_TodoModelTest:

    def test_create_and_retrieve_todo(self, session):
        new_todo = Todo(title="Buy groceries", complete=False)
        session.add(new_todo)
        session.commit()

        assert new_todo.id is not None

        fetched = session.query(Todo).filter_by(id=new_todo.id).first()
        assert fetched is not None
        assert fetched.title == "Buy groceries"
        assert fetched.complete is False

    def test_update_todo_completion_status(self, session):
        todo = Todo(title="Wash car", complete=False)
        session.add(todo)
        session.commit()

        fetched = session.query(Todo).filter_by(id=todo.id).first()
        fetched.complete = True
        session.commit()

        updated = session.query(Todo).filter_by(id=todo.id).first()
        assert updated.complete is True

    def test_delete_todo(self, session):
        todo = Todo(title="Pay bills", complete=False)
        session.add(todo)
        session.commit()

        fetched = session.query(Todo).filter_by(id=todo.id).first()
        session.delete(fetched)
        session.commit()

        deleted = session.query(Todo).filter_by(id=todo.id).first()
        assert deleted is None
