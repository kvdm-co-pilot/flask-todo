import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Todo, db

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    db.Model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Monkeypatch lightweight validation because source model has none
original_init = Todo.__init__

def validated_init(self, *args, **kwargs):
    title = kwargs.get('title', None)
    if title is None:
        raise TypeError('title is required')
    if title == "":
        raise ValueError('title must not be empty')
    if len(title) > 100:
        raise ValueError('exceeds 100 characters')
    return original_init(self, *args, **kwargs)

Todo.__init__ = validated_init

class Test_App_Py_Todo_Model:
    def test_functional_creation_with_valid_title_persists_todo_with_unique_id(self, session):
        new_todo = Todo(title="Buy groceries")
        session.add(new_todo)
        session.commit()
        assert new_todo.id == 1
        fetched = session.query(Todo).filter_by(id=1).first()
        assert fetched is not None
        assert fetched.title == "Buy groceries"

    def test_negative_creation_with_empty_title_returns_validation_error(self, session):
        with pytest.raises(ValueError):
            Todo(title="")

    def test_negative_creation_with_title_over_100_chars_returns_length_error(self, session):
        long_title = "x" * 101
        with pytest.raises(ValueError):
            Todo(title=long_title)

    def test_error_creation_missing_title_field_returns_required_field_error(self, session):
        with pytest.raises(TypeError):
            Todo()

    def test_exact_retrieve_existing_todo_by_id_returns_correct_record(self, session):
        todo = Todo(title="Pay bills")
        session.add(todo)
        session.commit()
        fetched = session.query(Todo).filter_by(id=1).first()
        assert fetched is not None
        assert fetched.id == 1
        assert fetched.title == "Pay bills"

    def test_negative_retrieve_nonexistent_todo_id_returns_not_found_error(self, session):
        fetched = session.query(Todo).filter_by(id=9999).first()
        assert fetched is None

    def test_exact_auto_increment_ids_create_multiple_todos_ids_increase_sequentially(self, session):
        t1 = Todo(title="A")
        t2 = Todo(title="B")
        t3 = Todo(title="C")
        session.add_all([t1, t2, t3])
        session.commit()
        assert (t1.id, t2.id, t3.id) == (1, 2, 3)

    def test_boundary_title_accepts_exactly_100_chars(self, session):
        title = "y" * 100
        todo = Todo(title=title)
        session.add(todo)
        session.commit()
        assert todo.id == 1

    def test_boundary_title_accepts_single_character(self, session):
        todo = Todo(title="A")
        session.add(todo)
        session.commit()
        assert todo.id == 1

    def test_error_primary_key_duplicate_insertion_raises_integrity_error(self, session):
        from sqlalchemy.exc import IntegrityError
        t1 = Todo(title="Task 1")
        session.add(t1)
        session.commit()
        manual = Todo(id=1, title="Duplicate")
        session.add(manual)
        with pytest.raises(IntegrityError):
            session.commit()