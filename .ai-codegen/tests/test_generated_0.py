import pytest
from unittest.mock import MagicMock, patch
from flask import Flask

import app as app_module


@pytest.fixture
def flask_app():
    return app_module.app


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_todo():
    todo = MagicMock()
    todo.id = 1
    todo.title = "Test Task"
    todo.completed = False
    todo.complete = False
    return todo


def test_add_valid_input_creates_record(flask_app, mock_db, mock_todo):
    with flask_app.test_request_context(
        "/add",
        method="POST",
        data={"title": "Test Task"}
    ), patch("app.db", mock_db), patch("app.Todo", return_value=mock_todo):
        from app import add

        result = add()

        mock_db.session.add.assert_called_once_with(mock_todo)
        mock_db.session.commit.assert_called_once()
        assert result is not None


def test_add_invalid_input_raises_error(flask_app, mock_db):
    with flask_app.test_request_context(
        "/add",
        method="POST",
        data={}
    ), patch("app.db", mock_db):
        from app import add

        with pytest.raises(Exception):
            add()


def test_update_existing_item_updates_fields(flask_app, mock_db, mock_todo):
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_todo

    with flask_app.test_request_context("/update/1"), patch("app.db", mock_db):
        from app import update

        update(1)

        assert mock_todo.complete is True
        mock_db.session.commit.assert_called_once()


def test_update_nonexistent_item_no_commit(flask_app, mock_db):
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = None

    with flask_app.test_request_context("/update/999"), patch("app.db", mock_db):
        from app import update

        result = update(999)

        assert result is None
        mock_db.session.commit.assert_not_called()


def test_delete_existing_item_deletes_record(flask_app, mock_db, mock_todo):
    mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_todo

    with flask_app.test_request_context("/delete/1"), patch("app.db", mock_db):
        from app import delete

        delete(1)

        mock_db.session.delete.assert_called_once_with(mock_todo)
        mock_db.session.commit.assert_called_once()