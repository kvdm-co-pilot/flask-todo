import pytest
import importlib
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_todo():
    todo = MagicMock()
    todo.id = 1
    todo.title = "Test Task"
    todo.complete = False
    return todo

def test_add_valid_input_creates_record(mock_db, mock_todo):
    with patch('app.SQLAlchemy', return_value=mock_db), patch('app.Todo', return_value=mock_todo):
        import app as app_module
        app_module = importlib.reload(app_module)
        from app import add

        with app_module.app.app_context():
            result = add("Test Task")

        mock_db.session.add.assert_called_once_with(mock_todo)
        mock_db.session.commit.assert_called_once()
        assert result is not None

def test_add_invalid_input_raises_error(mock_db):
    with patch('app.SQLAlchemy', return_value=mock_db):
        import app as app_module
        app_module = importlib.reload(app_module)
        from app import add

        with app_module.app.app_context():
            with pytest.raises(Exception):
                add(None)

def test_update_existing_item_updates_fields(mock_db, mock_todo):
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_todo
    with patch('app.SQLAlchemy', return_value=mock_db):
        import app as app_module
        app_module = importlib.reload(app_module)
        from app import update

        with app_module.app.app_context():
            update(1, title="Updated", complete=True)

        assert mock_todo.title == "Updated"
        assert mock_todo.complete is True
        mock_db.session.commit.assert_called_once()

def test_update_nonexistent_item_no_commit(mock_db):
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
    with patch('app.SQLAlchemy', return_value=mock_db):
        import app as app_module
        app_module = importlib.reload(app_module)
        from app import update

        with app_module.app.app_context():
            result = update(999, title="X")

        assert result is None
        mock_db.session.commit.assert_not_called()

def test_delete_existing_item_deletes_record(mock_db, mock_todo):
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_todo
    with patch('app.SQLAlchemy', return_value=mock_db):
        import app as app_module
        app_module = importlib.reload(app_module)
        from app import delete

        with app_module.app.app_context():
            delete(1)

        mock_db.session.delete.assert_called_once_with(mock_todo)
        mock_db.session.commit.assert_called_once()