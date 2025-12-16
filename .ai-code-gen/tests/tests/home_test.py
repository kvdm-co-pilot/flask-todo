from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pytest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Incomplete')

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    if not title:
        return jsonify(message='Title is required'), 400
    if len(title) > 100:
        return jsonify(message='Title is too long'), 400
    if Todo.query.filter_by(title=title).first():
        return jsonify(message='Duplicate ID'), 400
    new_todo = Todo(title=title)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('list_tasks'))

@app.route('/update', methods=['POST'])
def update_todo():
    old_title = request.form.get('old_title')
    new_title = request.form.get('new_title')
    todo = Todo.query.filter_by(title=old_title).first()
    if todo:
        todo.title = new_title
        db.session.commit()
        return redirect(url_for('list_tasks'))
    return jsonify(message='Todo not found'), 404

@app.route('/delete', methods=['POST'])
def delete_todo():
    title = request.form.get('title')
    todo = Todo.query.filter_by(title=title).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for('list_tasks'))
    return jsonify(message='Todo not found'), 404

@app.route('/toggle', methods=['POST'])
def toggle_todo():
    title = request.form.get('title')
    todo = Todo.query.filter_by(title=title).first()
    if todo:
        todo.status = 'Complete' if todo.status == 'Incomplete' else 'Incomplete'
        db.session.commit()
        return redirect(url_for('list_tasks'))
    return jsonify(message='Todo not found'), 404

@app.route('/tasks', methods=['GET'])
def list_tasks():
    todos = Todo.query.all()
    return jsonify([{'title': todo.title, 'status': todo.status} for todo in todos])

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.session.remove()
            db.drop_all()

class Functional_AddNewTodoWithValidTitleTest:
    def test_add_todo_with_valid_title(self, test_client):
        response = test_client.post('/add', data=dict(title='Complete project report'))
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title='Complete project report').first()
        assert status_code == 302
        assert new_todo is not None
        assert new_todo.title == 'Complete project report'

class Functional_UpdateTodoTitleTest:
    def test_update_todo_title(self, test_client):
        test_client.post('/add', data=dict(title='Buy groceries'))
        response = test_client.post('/update', data=dict(old_title='Buy groceries', new_title='Buy groceries and fruits'))
        status_code = response.status_code
        updated_todo = Todo.query.filter_by(title='Buy groceries and fruits').first()
        assert status_code == 302
        assert updated_todo is not None
        assert updated_todo.title == 'Buy groceries and fruits'

class Functional_DeleteExistingTodoTest:
    def test_delete_existing_todo(self, test_client):
        test_client.post('/add', data=dict(title='Attend meeting at 3 PM'))
        response = test_client.post('/delete', data=dict(title='Attend meeting at 3 PM'))
        status_code = response.status_code
        deleted_todo = Todo.query.filter_by(title='Attend meeting at 3 PM').first()
        assert status_code == 302
        assert deleted_todo is None

class Functional_ToggleTodoCompletionStatusTest:
    def test_toggle_completion_status(self, test_client):
        test_client.post('/add', data=dict(title='Read book'))
        response = test_client.post('/toggle', data=dict(title='Read book'))
        status_code = response.status_code
        toggled_todo = Todo.query.filter_by(title='Read book').first()
        assert status_code == 302
        assert toggled_todo is not None
        assert toggled_todo.status == 'Complete'

class Invariant_VerifyTitlePresenceTest:
    def test_title_presence(self, test_client):
        response = test_client.post('/add', data=dict(title=''))
        assert b'Title is required' in response.data

class Invariant_EnsureUniqueTodoIDTest:
    def test_unique_todo_id(self, test_client):
        test_client.post('/add', data=dict(title='Go for a run'))
        response = test_client.post('/add', data=dict(title='Go for a run'))
        assert b'Duplicate ID' in response.data

class StateTransition_ToggleCompletionStatusTest:
    def test_toggle_completion_status_with_commit_failure(self, test_client):
        test_client.post('/add', data=dict(title='Submit tax forms'))
        response = test_client.post('/toggle', data=dict(title='Submit tax forms'))
        assert b'Database commit failure' in response.data

class StateTransition_DeleteTaskTest:
    def test_delete_task_with_commit_failure(self, test_client):
        test_client.post('/add', data=dict(title='Clean kitchen'))
        response = test_client.post('/delete', data=dict(title='Clean kitchen'))
        assert b'Database commit failure' in response.data

class Boundary_TitleLengthMinimumTest:
    def test_title_length_minimum(self, test_client):
        response = test_client.post('/add', data=dict(title=''))
        assert b'Title is too short' in response.data

class Boundary_TitleLengthMaximumTest:
    def test_title_length_maximum(self, test_client):
        long_title = 'a' * 101
        response = test_client.post('/add', data=dict(title=long_title))
        assert b'Title is too long' in response.data

class Boundary_UniqueTaskIDCheckTest:
    def test_unique_task_id_check(self, test_client):
        test_client.post('/add', data=dict(title='Duplicate ID task'))
        response = test_client.post('/add', data=dict(title='Duplicate ID task'))
        assert b'Duplicate ID' in response.data

class Security_AddTaskSQLInjectionTest:
    def test_sql_injection(self, test_client):
        response = test_client.post('/add', data=dict(title="' OR '1'='1"))
        assert b'SQL injection prevented' in response.data

class Security_AddTaskXSSInjectionTest:
    def test_xss_injection(self, test_client):
        response = test_client.post('/add', data=dict(title='<script>alert("XSS")</script>'))
        assert b'XSS prevented' in response.data

class Security_DeleteTaskUnauthorizedAccessTest:
    def test_unauthorized_access(self, test_client):
        response = test_client.post('/delete', data=dict(title='Unauthorized attempt'))
        assert b'Unauthorized access' in response.data

class FailureRecovery_DatabaseCommitFailureOnToggleTest:
    def test_database_commit_failure_on_toggle(self, test_client):
        test_client.post('/add', data=dict(title='Backup data'))
        response = test_client.post('/toggle', data=dict(title='Backup data'))
        assert b'Commit failure' in response.data

class FailureRecovery_DatabaseCommitFailureOnDeleteTest:
    def test_database_commit_failure_on_delete(self, test_client):
        test_client.post('/add', data=dict(title='Delete temp files'))
        response = test_client.post('/delete', data=dict(title='Delete temp files'))
        assert b'Commit failure' in response.data

class FailureRecovery_InterruptedTaskCreationTest:
    def test_interrupted_task_creation(self, test_client):
        response = test_client.post('/add', data=dict(title='Draft proposal'))
        assert b'Creation interrupted' in response.data

class CrossEntity_TaskListingConsistencyTest:
    def test_task_listing_consistency(self, test_client):
        test_client.post('/add', data=dict(title='Task 1'))
        test_client.post('/add', data=dict(title='Task 2'))
        response = test_client.get('/tasks')
        status_code = response.status_code
        assert status_code == 200
        assert b'Task 1' in response.data
        assert b'Task 2' in response.data

class CrossEntity_TaskStateUpdateConsistencyTest:
    def test_task_state_update_consistency(self, test_client):
        test_client.post('/add', data=dict(title='Task State Test'))
        response = test_client.post('/update', data=dict(old_title='Task State Test', new_title='Task State Test Updated'))
        status_code = response.status_code
        assert status_code == 302
        updated_todo = Todo.query.filter_by(title='Task State Test Updated').first()
        assert updated_todo is not None
        assert updated_todo.status == 'Incomplete'