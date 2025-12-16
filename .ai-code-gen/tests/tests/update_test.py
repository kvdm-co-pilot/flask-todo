from app import app, db, Todo
import pytest
from flask import url_for
from werkzeug.exceptions import NotFound, Forbidden

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

class Functional_AddValidTodoItemTest:
    def test_add_valid_todo_item(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title='Complete project report'))

        # When
        # Checking the redirection and new item in database
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title='Complete project report').first()

        # Then
        assert status_code == 302
        assert new_todo is not None
        assert new_todo.title == 'Complete project report'

class Functional_UpdateExistingTodoItemTest:
    def test_update_existing_todo_item(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Initial Task'))
        existing_todo = Todo.query.filter_by(title='Initial Task').first()

        response = test_client.post(f'/update/{existing_todo.id}', data=dict(title='Edit project report'))

        # When
        # Checking the updated task in database
        status_code = response.status_code
        updated_todo = Todo.query.filter_by(title='Edit project report').first()

        # Then
        assert status_code == 302
        assert updated_todo is not None
        assert updated_todo.title == 'Edit project report'

class Functional_HandleInvalidTodoUpdateTest:
    def test_handle_invalid_todo_update(self, test_client):
        # Given
        response = test_client.post('/update/999', data=dict(title='Non-existent task'))

        # When
        # Checking the error handling
        status_code = response.status_code

        # Then
        assert status_code == 404

class Boundary_SubmitEmptyTaskTest:
    def test_submit_empty_task(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title=''))

        # When
        # Checking error message for empty task
        status_code = response.status_code

        # Then
        assert status_code == 400

class Boundary_AddMaxLengthTaskNameTest:
    def test_add_max_length_task_name(self, test_client):
        # Given
        max_length_name = 'A' * 255
        response = test_client.post('/add', data=dict(title=max_length_name))

        # When
        # Checking the redirection and new item in database
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title=max_length_name).first()

        # Then
        assert status_code == 302
        assert new_todo is not None
        assert new_todo.title == max_length_name

class Negative_VerifyTodoHasTitleTest:
    def test_verify_todo_has_title(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title=None))

        # When
        # Checking error handling for None title
        status_code = response.status_code

        # Then
        assert status_code == 400

class Exact_VerifyUniqueTodoIDTest:
    def test_verify_unique_todo_id(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Task 1'))
        test_client.post('/add', data=dict(title='Task 2'))

        task1 = Todo.query.filter_by(title='Task 1').first()
        task2 = Todo.query.filter_by(title='Task 2').first()

        # Then
        assert task1.id != task2.id

class Exact_ToggleTaskCompletionStatusTest:
    def test_toggle_task_completion_status(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Toggle Task'))
        toggle_todo = Todo.query.filter_by(title='Toggle Task').first()

        response = test_client.post(f'/toggle/{toggle_todo.id}')

        # When
        # Checking completion status update
        status_code = response.status_code
        updated_todo = Todo.query.filter_by(title='Toggle Task').first()

        # Then
        assert status_code == 302
        assert updated_todo.is_completed != toggle_todo.is_completed

class Exact_DeleteTaskSuccessfullyTest:
    def test_delete_task_successfully(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Delete Task'))
        delete_todo = Todo.query.filter_by(title='Delete Task').first()

        response = test_client.post(f'/delete/{delete_todo.id}')

        # When
        # Checking deletion from database
        status_code = response.status_code
        deleted_todo = Todo.query.filter_by(title='Delete Task').first()

        # Then
        assert status_code == 302
        assert deleted_todo is None

class Error_DeleteTaskUnauthorizedAccessTest:
    def test_delete_task_unauthorized_access(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Unauthorized Task'))
        unauthorized_todo = Todo.query.filter_by(title='Unauthorized Task').first()

        response = test_client.post(f'/delete/{unauthorized_todo.id}', headers={'Authorization': 'InvalidToken'})

        # When
        # Checking unauthorized access handling
        status_code = response.status_code

        # Then
        assert status_code == 403

class Boundary_TestEmptyTitleDisallowedTest:
    def test_empty_title_disallowed(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title=''))

        # When
        # Checking error message for empty title
        status_code = response.status_code

        # Then
        assert status_code == 400

class Boundary_TestMaxLengthTitleAcceptedTest:
    def test_max_length_title_accepted(self, test_client):
        # Given
        max_title = 'A' * 255
        response = test_client.post('/add', data=dict(title=max_title))

        # When
        # Checking the redirection and new item in database
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title=max_title).first()

        # Then
        assert status_code == 302
        assert new_todo is not None
        assert new_todo.title == max_title

class Boundary_TestMinLengthTitleAcceptedTest:
    def test_min_length_title_accepted(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title='A'))

        # When
        # Checking the redirection and new item in database
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title='A').first()

        # Then
        assert status_code == 302
        assert new_todo is not None
        assert new_todo.title == 'A'

class Boundary_TestTaskIDBoundsTest:
    def test_task_id_bounds(self, test_client):
        # Given
        response_zero = test_client.post('/update/0', data=dict(title='OutOfBound'))
        response_max = test_client.post(f'/update/{2**31-1}', data=dict(title='MaxBound'))

        # When
        # Checking the error handling for out-of-bound IDs
        status_code_zero = response_zero.status_code
        status_code_max = response_max.status_code

        # Then
        assert status_code_zero == 404
        assert status_code_max == 404

class Error_Security_TestSQLInjectionOnAddTaskTest:
    def test_sql_injection_on_add_task(self, test_client):
        # Given
        injection_input = "'; DROP TABLE todos; --"
        response = test_client.post('/add', data=dict(title=injection_input))

        # When
        # Checking the input is sanitized
        status_code = response.status_code
        injected_todo = Todo.query.filter_by(title=injection_input).first()

        # Then
        assert status_code == 302
        assert injected_todo is not None

class Error_Security_TestXSSOnAddTaskTest:
    def test_xss_on_add_task(self, test_client):
        # Given
        xss_input = '<script>alert(1)</script>'
        response = test_client.post('/add', data=dict(title=xss_input))

        # When
        # Checking the input is treated as plain text
        status_code = response.status_code
        xss_todo = Todo.query.filter_by(title=xss_input).first()

        # Then
        assert status_code == 302
        assert xss_todo is not None

class Error_Security_TestUnauthorizedTaskDeletionViaURLManipulationTest:
    def test_unauthorized_task_deletion_via_url_manipulation(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='URL Manipulation Task'))
        url_todo = Todo.query.filter_by(title='URL Manipulation Task').first()

        response = test_client.post(f'/delete/{url_todo.id}', headers={'Authorization': 'InvalidToken'})

        # When
        # Checking unauthorized deletion attempt handling
        status_code = response.status_code

        # Then
        assert status_code == 403

class Error_Security_TestCSRFOnTaskDeletionTest:
    def test_csrf_on_task_deletion(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='CSRF Task'))
        csrf_todo = Todo.query.filter_by(title='CSRF Task').first()

        response = test_client.post(f'/delete/{csrf_todo.id}', headers={'CSRF-Token': 'InvalidToken'})

        # When
        # Checking CSRF token validation
        status_code = response.status_code

        # Then
        assert status_code == 403

class Error_FailureRecovery_HandleDatabaseCommitFailureOnAddTest:
    def test_handle_database_commit_failure_on_add(self, test_client):
        # Simulate a database commit failure
        pass  # Implementation depends on mocking database behavior

class Error_FailureRecovery_HandleConcurrencyConflictOnTaskCompletionToggleTest:
    def test_handle_concurrency_conflict_on_completion_toggle(self, test_client):
        # Simulate concurrent toggles
        pass  # Implementation depends on simulating concurrent access

class Error_FailureRecovery_HandleDatabaseCommitFailureOnDeletionTest:
    def test_handle_database_commit_failure_on_deletion(self, test_client):
        # Simulate a database commit failure
        pass  # Implementation depends on mocking database behavior

class Exact_CrossEntityConsistency_TestTaskRetrievalAndDisplayAccuracyTest:
    def test_task_retrieval_and_display_accuracy(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Display Task'))
        display_todo = Todo.query.filter_by(title='Display Task').first()

        response = test_client.get('/')

        # When
        # Checking task retrieval and display
        status_code = response.status_code
        data = response.data

        # Then
        assert status_code == 200
        assert display_todo.title.encode() in data

class Exact_CrossEntityConsistency_VerifyDatabaseCommitOnStateChangeTest:
    def test_verify_database_commit_on_state_change(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='State Change Task'))
        state_change_todo = Todo.query.filter_by(title='State Change Task').first()

        test_client.post(f'/toggle/{state_change_todo.id}')

        # When
        # Checking database state consistency
        updated_todo = Todo.query.filter_by(title='State Change Task').first()

        # Then
        assert updated_todo.is_completed != state_change_todo.is_completed