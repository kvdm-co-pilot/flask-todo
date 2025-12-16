import pytest
from flask import Flask
from myproject.app import create_app, db
from myproject.models import Task

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class Functional_HomePageAccess_SuccessTest:
    def test_home_page_access_success(self, client):
        # Given
        
        # When
        response = client.get('/')

        # Then
        assert response.status_code == 200
        assert b"Welcome" in response.data

class Functional_HomePageAccess_ServerOfflineTest:
    @pytest.mark.skip(reason="Cannot simulate server offline in unit test")
    def test_home_page_access_server_offline(self, client):
        # This test is skipped because server state cannot be changed in a unit test environment
        pass

class Functional_HomePageAccess_InvalidHTTPMethodTest:
    def test_home_page_access_invalid_http_method(self, client):
        # Given
        
        # When
        response = client.post('/')

        # Then
        assert response.status_code == 405

class Functional_HomePageAccess_LargeURLLengthTest:
    def test_home_page_access_large_url_length(self, client):
        # Given
        long_url = '/' + 'a' * 2048

        # When
        response = client.get(long_url)

        # Then
        assert response.status_code == 200
        assert b"Welcome" in response.data

class Functional_HomePageAccess_HighTrafficTest:
    @pytest.mark.skip(reason="Simulating high traffic requires integration testing")
    def test_home_page_access_high_traffic(self):
        # This test is skipped because simulating high traffic is not feasible in unit tests
        pass

class Invariant_VerifyUniqueTaskIDTest:
    def test_verify_unique_task_id(self, client):
        # Given
        task_data1 = {'title': 'Task 1'}
        task_data2 = {'title': 'Task 2'}
        client.post('/tasks', json=task_data1)
        client.post('/tasks', json=task_data2)

        # When
        task1 = Task.query.filter_by(title='Task 1').first()
        task2 = Task.query.filter_by(title='Task 2').first()

        # Then
        assert task1.id != task2.id

class Invariant_VerifyTaskTitleLengthTest:
    def test_verify_task_title_length(self, client):
        # Given
        valid_title = 'a' * 50
        invalid_title = 'a' * 256

        # When
        response_valid = client.post('/tasks', json={'title': valid_title})
        response_invalid = client.post('/tasks', json={'title': invalid_title})

        # Then
        assert response_valid.status_code == 201
        assert response_invalid.status_code == 400

class Invariant_VerifyTaskCompletionStatusBooleanTest:
    def test_verify_task_completion_status_boolean(self, client):
        # Given
        task_data = {'title': 'Test Task', 'completed': False}
        client.post('/tasks', json=task_data)

        # When
        task = Task.query.filter_by(title='Test Task').first()

        # Then
        assert isinstance(task.completed, bool)

class StateTransition_TestMarkTaskAsCompleteTest:
    def test_mark_task_as_complete(self, client):
        # Given
        task_data = {'title': 'Incomplete Task', 'completed': False}
        client.post('/tasks', json=task_data)
        task = Task.query.filter_by(title='Incomplete Task').first()

        # When
        response = client.patch(f'/tasks/{task.id}', json={'completed': True})

        # Then
        assert response.status_code == 200
        assert task.completed is True

class StateTransition_TestTaskDeletionTest:
    def test_task_deletion(self, client):
        # Given
        task_data = {'title': 'Task to Delete'}
        client.post('/tasks', json=task_data)
        task = Task.query.filter_by(title='Task to Delete').first()

        # When
        response = client.delete(f'/tasks/{task.id}')

        # Then
        assert response.status_code == 200
        assert Task.query.get(task.id) is None

class DomainBoundary_TestTaskTitleMinLengthTest:
    def test_task_title_min_length(self, client):
        # Given
        min_length_title = 'a'

        # When
        response = client.post('/tasks', json={'title': min_length_title})

        # Then
        assert response.status_code == 201

class DomainBoundary_TestTaskTitleMaxLengthTest:
    def test_task_title_max_length(self, client):
        # Given
        max_length_title = 'a' * 255

        # When
        response = client.post('/tasks', json={'title': max_length_title})

        # Then
        assert response.status_code == 201

class DomainBoundary_TestEmptyTaskTitleTest:
    def test_empty_task_title(self, client):
        # Given
        empty_title = ''

        # When
        response = client.post('/tasks', json={'title': empty_title})

        # Then
        assert response.status_code == 400

class DomainBoundary_TestTaskCompletionStatusMinValueTest:
    def test_task_completion_status_min_value(self, client):
        # Given
        task_data = {'title': 'Test Task', 'completed': False}
        client.post('/tasks', json=task_data)

        # When
        task = Task.query.filter_by(title='Test Task').first()

        # Then
        assert task.completed is False

class DomainBoundary_TestTaskCompletionStatusMaxValueTest:
    def test_task_completion_status_max_value(self, client):
        # Given
        task_data = {'title': 'Test Task', 'completed': True}
        client.post('/tasks', json=task_data)

        # When
        task = Task.query.filter_by(title='Test Task').first()

        # Then
        assert task.completed is True

class DomainBoundary_TestTaskCompletionStatusNoneValueTest:
    def test_task_completion_status_none_value(self, client):
        # Given
        task_data = {'title': 'Test Task', 'completed': None}

        # When
        response = client.post('/tasks', json=task_data)

        # Then
        assert response.status_code == 400

class Security_TestAddTaskForSQLInjectionTest:
    def test_add_task_for_sql_injection(self, client):
        # Given
        sql_injection_title = "'); DROP TABLE tasks;--"

        # When
        response = client.post('/tasks', json={'title': sql_injection_title})

        # Then
        assert response.status_code == 400

class Security_TestUpdateTaskCompletionStatusUnauthorizedChangeTest:
    def test_update_task_completion_status_unauthorized_change(self, client):
        # Given
        task_data = {'title': 'Unauthorized Task', 'completed': False}
        client.post('/tasks', json=task_data)
        task = Task.query.filter_by(title='Unauthorized Task').first()

        # When
        response = client.patch(f'/tasks/{task.id}', json={'completed': True})

        # Then
        assert response.status_code == 403

class Security_TestDeleteTaskUnauthorizedAccessTest:
    def test_delete_task_unauthorized_access(self, client):
        # Given
        task_data = {'title': 'Unauthorized Task'}
        client.post('/tasks', json=task_data)
        task = Task.query.filter_by(title='Unauthorized Task').first()

        # When
        response = client.delete(f'/tasks/{task.id}')

        # Then
        assert response.status_code == 403

class FailureRecovery_TestDatabaseCommitFailureOnTaskCompleteTest:
    @pytest.mark.skip(reason="Database commit failure simulation requires integration testing")
    def test_database_commit_failure_on_task_complete(self):
        # This test is skipped because simulating database failures requires integration testing
        pass

class FailureRecovery_TestDatabaseCommitFailureOnTaskDeletionTest:
    @pytest.mark.skip(reason="Database commit failure simulation requires integration testing")
    def test_database_commit_failure_on_task_deletion(self):
        # This test is skipped because simulating database failures requires integration testing
        pass

class FailureRecovery_TestInterruptionDuringTaskAdditionTest:
    @pytest.mark.skip(reason="Interruption simulation requires integration testing")
    def test_interruption_during_task_addition(self):
        # This test is skipped because simulating system interruptions requires integration testing
        pass

class FailureRecovery_TestInterruptionDuringTaskUpdateTest:
    @pytest.mark.skip(reason="Interruption simulation requires integration testing")
    def test_interruption_during_task_update(self):
        # This test is skipped because simulating system interruptions requires integration testing
        pass

class CrossEntityConsistency_VerifyTaskListReflectsUserActionsTest:
    def test_verify_task_list_reflects_user_actions(self, client):
        # Given
        task_data1 = {'title': 'Task 1'}
        task_data2 = {'title': 'Task 2'}
        client.post('/tasks', json=task_data1)
        client.post('/tasks', json=task_data2)

        # When
        response = client.get('/tasks')

        # Then
        assert response.status_code == 200
        tasks = response.get_json()
        assert len(tasks) == 2
        assert tasks[0]['title'] == 'Task 1'
        assert tasks[1]['title'] == 'Task 2'