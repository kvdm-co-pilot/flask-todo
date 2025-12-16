# app.py

from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


@app.route("/")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    if not title:
        abort(400, description="Title cannot be empty")
    if len(title) > 100:
        abort(400, description="Title length exceeds limit")
    try:
        new_todo = Todo(title=title, complete=False)
        db.session.add(new_todo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Database error occurred")
    return redirect(url_for("home"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        abort(404, description="Task does not exist")
    try:
        todo.complete = not todo.complete
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Database error occurred")
    return redirect(url_for("home"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = db.session.get(Todo, todo_id)
    if not todo:
        abort(404, description="Task does not exist")
    # Simulate unauthorized access check
    if False:  # Replace with actual authorization logic
        abort(403, description="Access denied")
    try:
        db.session.delete(todo)
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(500, description="Database error occurred")
    return redirect(url_for("home"))


# test_app.py

import pytest
from app import app, db, Todo
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_functional_add_valid_task(client):
    # Given
    initial_count = Todo.query.count()
    data = {'title': 'Buy groceries'}

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 200
    assert Todo.query.count() == initial_count + 1
    assert b'Buy groceries' in response.data


def test_functional_update_task_completion_status(client):
    # Given
    todo_item = Todo(title='Buy groceries', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    response = client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

    # Then
    assert response.status_code == 200
    updated_item = db.session.get(Todo, todo_item.id)
    assert updated_item.complete is True


def test_functional_delete_existing_task(client):
    # Given
    todo_item = Todo(title='Buy groceries', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    initial_count = Todo.query.count()

    # When
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

    # Then
    assert response.status_code == 200
    assert Todo.query.count() == initial_count - 1


def test_functional_add_task_without_title(client):
    # Given
    data = {'title': ''}

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 400
    assert b'Title cannot be empty' in response.data


def test_functional_add_task_with_large_title(client):
    # Given
    data = {'title': 'x' * 101}

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 400
    assert b'Title length exceeds limit' in response.data


def test_functional_update_non_existent_task(client):
    # Given
    non_existent_id = 9999

    # When
    response = client.get(url_for('update', todo_id=non_existent_id), follow_redirects=True)

    # Then
    assert response.status_code == 404
    assert b'Task does not exist' in response.data


def test_functional_delete_non_existent_task(client):
    # Given
    non_existent_id = 9999

    # When
    response = client.get(url_for('delete', todo_id=non_existent_id), follow_redirects=True)

    # Then
    assert response.status_code == 404
    assert b'Task does not exist' in response.data


def test_invariant_unique_todo_id(client):
    # Given
    task_titles = ['Task 1', 'Task 2', 'Task 3']

    # When
    for title in task_titles:
        client.post(url_for('add'), data={'title': title})

    # Then
    tasks = Todo.query.all()
    task_ids = [task.id for task in tasks]
    assert len(task_ids) == len(set(task_ids))


def test_invariant_todo_title_max_length(client):
    # Given
    data = {'title': 'x' * 100}

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 200
    assert b'x' * 100 in response.data


def test_invariant_todo_completion_status_boolean(client):
    # Given
    todo_item = Todo(title='Sample Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    retrieved_item = db.session.get(Todo, todo_item.id)

    # Then
    assert isinstance(retrieved_item.complete, bool)


def test_state_transition_todo_completion_status_change(client):
    # Given
    todo_item = Todo(title='Toggle Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

    # Then
    updated_item = db.session.get(Todo, todo_item.id)
    assert updated_item.complete is True

    # When
    client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

    # Then
    reverted_item = db.session.get(Todo, todo_item.id)
    assert reverted_item.complete is False


def test_state_transition_todo_deletion(client):
    # Given
    todo_item = Todo(title='Delete Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()
    initial_count = Todo.query.count()

    # When
    client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

    # Then
    assert Todo.query.count() == initial_count - 1


def test_boundary_todo_title_length_min(client):
    # Given
    data = {'title': 'a'}

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 200
    assert b'a' in response.data


def test_boundary_todo_title_length_max(client):
    # Given
    data = {'title': 'x' * 100}

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 200
    assert b'x' * 100 in response.data


def test_boundary_todo_id_positive_integer(client):
    # Given
    todo_item = Todo(title='Positive ID Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    retrieved_item = db.session.get(Todo, todo_item.id)

    # Then
    assert retrieved_item.id > 0


def test_boundary_todo_completion_status_true(client):
    # Given
    todo_item = Todo(title='True Status Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

    # Then
    updated_item = db.session.get(Todo, todo_item.id)
    assert updated_item.complete is True


def test_boundary_todo_completion_status_false(client):
    # Given
    todo_item = Todo(title='False Status Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # When
    retrieved_item = db.session.get(Todo, todo_item.id)

    # Then
    assert retrieved_item.complete is False


def test_negative_security_todo_addition_sql_injection(client):
    # Given
    data = {'title': "'; DROP TABLE Todo; --"}

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 400
    assert b'Database integrity maintained' in response.data


def test_negative_security_todo_deletion_unauthorized_access(client):
    # Given
    todo_item = Todo(title='Unauthorized Access', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # Simulating unauthorized HTTP request for deletion
    # When
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

    # Then
    assert response.status_code == 403
    assert b'Access denied' in response.data


def test_error_failure_recovery_add_task_database_failure(client):
    # Given
    data = {'title': 'Database Failure Task'}

    # Simulating database connection failure
    db.session.rollback()

    # When
    response = client.post(url_for('add'), data=data, follow_redirects=True)

    # Then
    assert response.status_code == 500
    assert b'Database error occurred' in response.data


def test_error_failure_recovery_update_task_database_failure(client):
    # Given
    todo_item = Todo(title='Update Failure Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # Simulating database failure
    db.session.rollback()

    # When
    response = client.get(url_for('update', todo_id=todo_item.id), follow_redirects=True)

    # Then
    assert response.status_code == 500
    assert b'Database error occurred' in response.data


def test_error_failure_recovery_delete_task_database_failure(client):
    # Given
    todo_item = Todo(title='Delete Failure Task', complete=False)
    db.session.add(todo_item)
    db.session.commit()

    # Simulating database failure
    db.session.rollback()

    # When
    response = client.get(url_for('delete', todo_id=todo_item.id), follow_redirects=True)

    # Then
    assert response.status_code == 500
    assert b'Database error occurred' in response.data


def test_consistency_todo_list_retrieval_and_display(client):
    # Given
    tasks = ['Task 1', 'Task 2', 'Task 3']
    for task in tasks:
        client.post(url_for('add'), data={'title': task})

    # When
    response = client.get(url_for('home'))

    # Then
    assert response.status_code == 200
    for task in tasks:
        assert task.encode() in response.data