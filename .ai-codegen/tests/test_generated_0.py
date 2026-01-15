import pytest
from unittest.mock import patch
import app

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as c:
        yield c

def test_create_todo_valid_title_expected_fields():
    title = 'Buy milk'
    todo = app.Todo(title=title, complete=False)
    assert todo.id is None
    assert todo.title == 'Buy milk'
    assert todo.complete is False

def test_create_todo_empty_title_expected_saved():
    title = ''
    todo = app.Todo(title=title, complete=False)
    assert todo.title == ''
    assert todo.complete is False

def test_toggle_complete_false_to_true():
    todo = app.Todo(title='x', complete=False)
    todo.complete = not todo.complete
    assert todo.complete is True

def test_toggle_complete_true_to_false():
    todo = app.Todo(title='x', complete=True)
    todo.complete = not todo.complete
    assert todo.complete is False

@patch('app.Todo.query', autospec=True)
def test_home_with_three_items(mock_query, client):
    mock_query.all.return_value = [app.Todo(title='a'), app.Todo(title='b'), app.Todo(title='c')]
    response = client.get('/')
    mock_query.all.assert_called_once()
    assert response.status_code == 200

@patch('app.Todo.query', autospec=True)
def test_home_with_no_items(mock_query, client):
    mock_query.all.return_value = []
    response = client.get('/')
    mock_query.all.assert_called_once()
    assert response.status_code == 200

@patch('app.db.session.commit')
@patch('app.Todo.query', autospec=True)
def test_update_toggle_false_to_true(mock_query, mock_commit, client):
    todo = app.Todo(title='x', complete=False)
    mock_query.filter_by.return_value.first.return_value = todo
    response = client.get('/update/1')
    assert todo.complete is True
    mock_commit.assert_called_once()
    assert response.status_code == 302

@patch('app.db.session.commit')
@patch('app.Todo.query', autospec=True)
def test_update_toggle_true_to_false(mock_query, mock_commit, client):
    todo = app.Todo(title='x', complete=True)
    mock_query.filter_by.return_value.first.return_value = todo
    response = client.get('/update/2')
    assert todo.complete is False
    mock_commit.assert_called_once()
    assert response.status_code == 302

@patch('app.Todo.query', autospec=True)
def test_update_non_existing_raises(mock_query, client):
    mock_query.filter_by.return_value.first.return_value = None
    with pytest.raises(Exception):
        client.get('/update/999')

@patch('app.db.session.add')
@patch('app.db.session.commit')
def test_add_valid_title_creates_todo(mock_commit, mock_add, client):
    response = client.post('/add', data={'title': 'Walk dog'})
    mock_add.assert_called_once()
    mock_commit.assert_called_once()
    assert response.status_code == 302

@patch('app.db.session.add')
@patch('app.db.session.commit')
def test_add_empty_title_creates_todo(mock_commit, mock_add, client):
    response = client.post('/add', data={'title': ''})
    mock_add.assert_called_once()
    mock_commit.assert_called_once()
    assert response.status_code == 302

@patch('app.db.session.add')
@patch('app.db.session.commit')
def test_add_missing_title_creates_none_title(mock_commit, mock_add, client):
    response = client.post('/add')
    mock_add.assert_called_once()
    mock_commit.assert_called_once()
    assert response.status_code == 302

@patch('app.db.session.delete')
@patch('app.db.session.commit')
@patch('app.Todo.query', autospec=True)
def test_delete_existing(mock_query, mock_commit, mock_delete, client):
    todo = app.Todo(title='x')
    mock_query.filter_by.return_value.first.return_value = todo
    response = client.get('/delete/3')
    mock_delete.assert_called_with(todo)
    mock_commit.assert_called_once()
    assert response.status_code == 302

@patch('app.db.session.delete')
@patch('app.Todo.query', autospec=True)
def test_delete_non_existing_raises(mock_query, mock_delete, client):
    mock_query.filter_by.return_value.first.return_value = None
    with pytest.raises(Exception):
        client.get('/delete/500')

def test_todo_initial_state_default_complete_false():
    todo = app.Todo(title='test', complete=False)
    assert todo.complete is False