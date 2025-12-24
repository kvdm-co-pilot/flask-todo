import pytest
import types

# Import the Flask app module that contains the toggle logic
import app

# The class name must be unique and derived from the entity under test
class ToggleTodoCompleteTest:

    @pytest.fixture
    def fake_todo(self):
        # Create a fake Todo object with a 'complete' attribute
        obj = types.SimpleNamespace()
        obj.complete = False
        return obj

    @pytest.fixture
    def fake_query(self, fake_todo):
        # Fake query object with filter_by().first() chain
        class FakeQuery:
            def filter_by(self, **kwargs):
                return self
            def first(self):
                return fake_todo
        return FakeQuery()

    @pytest.fixture
    def patched_todo_model(self, monkeypatch, fake_query):
        # Patch Todo.query to return our fake query
        class FakeTodoModel:
            query = fake_query
        monkeypatch.setattr(app, "Todo", FakeTodoModel)
        return FakeTodoModel

    @pytest.fixture
    def patched_db(self, monkeypatch):
        # Patch db.session.commit so it doesn't touch a real database
        class FakeSession:
            def commit(self):
                self.committed = True
        class FakeDB:
            session = FakeSession()
        monkeypatch.setattr(app, "db", FakeDB)
        return FakeDB

    def test_toggle_complete_redirects(self, monkeypatch, patched_todo_model, patched_db, fake_todo):
        # Patch url_for to return a fixed string
        monkeypatch.setattr(app, "url_for", lambda endpoint: "/home")

        # Patch redirect to return the input directly so we can assert on it
        monkeypatch.setattr(app, "redirect", lambda url: url)

        # Given the initial value
        initial_value = fake_todo.complete

        # When calling the function
        result = app.toggle_todo_complete(1)

        # Then - verifying toggle
        expected_complete = True
        assert fake_todo.complete == expected_complete

        # Then - verifying redirect target
        assert result == "/home"

        # Then - verifying commit was called
        assert patched_db.session.committed is True
