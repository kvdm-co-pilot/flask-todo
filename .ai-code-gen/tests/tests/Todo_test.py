import pytest
from app import db, Todo, app as flask_app

class App_Todo_Model_FullTest:
    def setup_method(self):
        # Enter app context
        self.ctx = flask_app.app_context()
        self.ctx.push()

        # Ensure tables exist
        db.create_all()

        # Clean DB
        db.session.rollback()
        for t in Todo.query.all():
            db.session.delete(t)
        db.session.commit()

    def teardown_method(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_functional_creation_with_valid_title_under_100_chars(self):
        title = "Buy milk"
        todo = Todo(title=title)
        db.session.add(todo)
        db.session.commit()
        assert todo.id is not None
        assert todo.title == "Buy milk"

    def test_negative_creation_with_empty_string_title_rejected(self):
        with pytest.raises(ValueError) as exc:
            Todo(title="")
        assert "title" in str(exc.value)

    def test_negative_creation_with_null_title_rejected(self):
        with pytest.raises(ValueError) as exc:
            Todo(title=None)
        assert "title" in str(exc.value)

    def test_boundary_creation_with_title_exactly_100_chars(self):
        title = "x" * 100
        todo = Todo(title=title)
        db.session.add(todo)
        db.session.commit()
        assert todo.id is not None
        assert len(todo.title) == 100

    def test_boundary_creation_with_title_101_chars_rejected(self):
        title = "x" * 101
        with pytest.raises(ValueError) as exc:
            Todo(title=title)
        assert "100" in str(exc.value)
