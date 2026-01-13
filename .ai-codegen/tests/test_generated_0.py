import pytest
from unittest.mock import MagicMock, patch

# Assuming module structure: from app import add, home, update, delete, Todo, db, app

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_todo():
    todo = MagicMock()
    todo.id = 1
    todo.title = "Test Task"
    todo.completed = False
    return todo


def test_add_valid_input_creates_record(mock_db, mock_todo):
    # Arrange
    with patch('app.db', mock_db), patch('app.Todo', return_value=mock_todo):
        from app import add

        # Act
        result = add("Test Task")

        # Assert
        mock_db.session.add.assert_called_once_with(mock_todo)
        mock_db.session.commit.assert_called_once()
        assert result is not None


def test_add_invalid_input_raises_error(mock_db):
    # Arrange
    with patch('app.db', mock_db):
        from app import add

        # Act / Assert
        with pytest.raises(Exception):
            add(None)


def test_update_existing_item_updates_fields(mock_db, mock_todo):
    # Arrange
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_todo
    with patch('app.db', mock_db):
        from app import update

        # Act
        update(1, title="Updated", completed=True)

        # Assert
        assert mock_todo.title == "Updated"
        assert mock_todo.completed is True
        mock_db.session.commit.assert_called_once()


def test_update_nonexistent_item_no_commit(mock_db):
    # Arrange
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = None
    with patch('app.db', mock_db):
        from app import update

        # Act
        result = update(999, title="X")

        # Assert
        assert result is None
        mock_db.session.commit.assert_not_called()


def test_delete_existing_item_deletes_record(mock_db, mock_todo):
    # Arrange
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_todo
    with patch('app.db', mock_db):
        from app import delete

        # Act
        delete(1)

        # Assert
        mock_db.session.delete.assert_called_once_with(mock_todo)
        mock_db.session.commit.assert_called_once()