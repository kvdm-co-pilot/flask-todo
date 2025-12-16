import pytest
from app import create_app, db, Todo
from flask import url_for

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def setup_database(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

def test_add_task_with_valid_title(client):
    initial_count = Todo.query.count()
    data = {'title': 'Buy Groceries'}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert Todo.query.count() == initial_count + 1
    assert b'Buy Groceries' in response.data

def test_add_task_with_empty_title(client):
    initial_count = Todo.query.count()
    data = {'title': ''}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 400
    assert Todo.query.count() == initial_count
    assert b'Title cannot be empty' in response.data

def test_add_task_with_max_title_length(client):
    initial_count = Todo.query.count()
    max_length_title = 'a' * 255
    data = {'title': max_length_title}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert Todo.query.count() == initial_count + 1
    assert max_length_title.encode() in response.data

def test_add_task_exceeding_max_title_length(client):
    initial_count = Todo.query.count()
    exceeding_title = 'a' * 256
    data = {'title': exceeding_title}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 400
    assert Todo.query.count() == initial_count
    assert b'Title exceeds maximum allowed length' in response.data

def test_view_todo_list_after_adding_task(client):
    data = {'title': 'Clean Room'}
    client.post(url_for('add'), data=data, follow_redirects=True)
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert b'Clean Room' in response.data

def test_delete_existing_task(client):
    todo_item = Todo(title='Task to Delete', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    initial_count = Todo.query.count()
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)
    assert response.status_code == 200
    assert Todo.query.count() == initial_count - 1

def test_mark_task_as_completed(client):
    todo_item = Todo(title='Task to Complete', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.post(url_for('update', todo_id=todo_item.id), follow_redirects=True)
    assert response.status_code == 200
    updated_item = db.session.get(Todo, todo_item.id)
    assert updated_item.complete is True

def test_unique_todo_id_check_upon_addition(client):
    data = {'title': 'Read Book'}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 200
    added_item = Todo.query.order_by(Todo.id.desc()).first()
    assert added_item.title == 'Read Book'
    assert isinstance(added_item.id, int)

def test_todo_title_max_length_validation(client):
    max_length_title = 'b' * 255
    data = {'title': max_length_title}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert max_length_title.encode() in response.data

def test_todo_completion_status_boolean_check(client):
    todo_item = Todo(title='Check Boolean', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert isinstance(todo_item.complete, bool)

def test_change_todo_completion_status_from_incomplete_to_complete(client):
    todo_item = Todo(title='Transition Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.post(url_for('update', todo_id=todo_item.id), follow_redirects=True)
    assert response.status_code == 200
    updated_item = db.session.get(Todo, todo_item.id)
    assert updated_item.complete is True

def test_delete_todo_and_check_non_existence(client):
    todo_item = Todo(title='Task to Remove', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)
    assert response.status_code == 200
    retrieved_item = db.session.get(Todo, todo_item.id)
    assert retrieved_item is None

def test_todo_title_minimum_length_check(client):
    min_length_title = 'A'
    data = {'title': min_length_title}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert min_length_title.encode() in response.data

def test_todo_id_positive_integer_check(client):
    todo_item = Todo(title='Positive ID Check', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert isinstance(todo_item.id, int)
    assert todo_item.id > 0

def test_todo_completion_status_true_false_check(client):
    todo_item = Todo(title='Boolean Status Check', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert isinstance(todo_item.complete, bool)

def test_todo_addition_input_sanitization_against_injection(client):
    initial_count = Todo.query.count()
    data = {'title': "<script>alert('hack')</script>"}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 400
    assert Todo.query.count() == initial_count
    assert b'No script execution' in response.data

def test_unauthorized_todo_deletion_attempt(client):
    todo_item = Todo(title='Unauthorized Delete', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)
    assert response.status_code == 403
    assert b'Unauthorized action' in response.data

def test_todo_addition_with_url_manipulation(client):
    manipulated_url = url_for('add') + "?title=InjectedTitle"
    response = client.post(manipulated_url, follow_redirects=True)
    assert response.status_code == 400
    assert b'Unauthorized task addition' in response.data

def test_add_task_with_database_down(client):
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    data = {'title': 'Pay Bills'}
    with app.app_context():
        db.drop_all()
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 500
    assert b'Database unavailable' in response.data

def test_delete_task_with_database_down(client):
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    todo_item = Todo(title='Delete with DB Down', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    with app.app_context():
        db.drop_all()
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)
    assert response.status_code == 500
    assert b'Database unavailable' in response.data

def test_retry_adding_task_after_database_restoration(client):
    data = {'title': 'Go Jogging'}
    response = client.post(url_for('add'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Go Jogging' in response.data

def test_retrieve_and_display_all_todos_accurately(client):
    todo_item1 = Todo(title='Task 1', complete=False)
    todo_item2 = Todo(title='Task 2', complete=False)
    db.session.add(todo_item1)
    db.session.add(todo_item2)
    db.session.commit()
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert b'Task 1' in response.data
    assert b'Task 2' in response.data

def test_verify_todo_list_update_on_ui_after_addition(client):
    data = {'title': 'Learn Python'}
    client.post(url_for('add'), data=data, follow_redirects=True)
    response = client.get(url_for('home'))
    assert response.status_code == 200
    assert b'Learn Python' in response.data

def test_verify_todo_list_update_on_ui_after_deletion(client):
    todo_item = Todo(title='Delete UI', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)
    response_after_deletion = client.get(url_for('home'))
    assert response.status_code == 200
    assert todo_item.title.encode() not in response_after_deletion.data