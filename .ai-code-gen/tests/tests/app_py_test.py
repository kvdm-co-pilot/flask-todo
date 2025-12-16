from app import app, db, Todo
import pytest

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client

class Functional_AddValidTodoItemTest:

    def test_add_valid_todo_item(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title='Buy groceries'))

        # When
        new_todo = Todo.query.filter_by(title='Buy groceries').first()

        # Then
        assert response.status_code == 302
        assert new_todo is not None
        assert new_todo.title == 'Buy groceries'

class Functional_UpdateTodoItemStatusTest:

    def test_update_todo_item_status(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Sample Task'))
        todo = Todo.query.filter_by(title='Sample Task').first()

        # When
        test_client.post(f'/update/{todo.id}', data={})
        updated_todo = Todo.query.filter_by(id=todo.id).first()

        # Then
        assert updated_todo.complete is True

class Functional_DeleteExistingTodoItemTest:

    def test_delete_existing_todo_item(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Task to Delete'))
        todo = Todo.query.filter_by(title='Task to Delete').first()

        # When
        test_client.post(f'/delete/{todo.id}', data={})
        deleted_todo = Todo.query.filter_by(id=todo.id).first()

        # Then
        assert deleted_todo is None

class Functional_AddTodoItemEmptyTitleTest:

    def test_add_todo_item_empty_title(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title=''))

        # When
        todos = Todo.query.all()

        # Then
        assert response.status_code == 302
        assert len(todos) == 0

class Functional_UpdateNonExistentTodoItemTest:

    def test_update_non_existent_todo_item(self, test_client):
        # Given
        non_existent_id = 9999

        # When & Then
        response = test_client.post(f'/update/{non_existent_id}', data={})
        assert response.status_code == 404

class Functional_DeleteNonExistentTodoItemTest:

    def test_delete_non_existent_todo_item(self, test_client):
        # Given
        non_existent_id = 9999

        # When & Then
        response = test_client.post(f'/delete/{non_existent_id}', data={})
        assert response.status_code == 404

class Invariant_VerifyTodoItemHasTitleTest:

    def test_verify_todo_item_has_title(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Check Title'))

        # When
        todos = Todo.query.all()

        # Then
        for todo in todos:
            assert todo.title != ''

class Boundary_VerifyUniqueTodoIDTest:

    def test_verify_unique_todo_id(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='First Task'))
        test_client.post('/add', data=dict(title='Second Task'))

        # When
        first_todo = Todo.query.filter_by(title='First Task').first()
        second_todo = Todo.query.filter_by(title='Second Task').first()

        # Then
        assert first_todo.id != second_todo.id

class StateTransition_ToggleTaskCompletionStatusTest:

    def test_toggle_task_completion_status(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Toggle Task'))
        todo = Todo.query.filter_by(title='Toggle Task').first()

        # First toggle
        test_client.post(f'/update/{todo.id}', data={})
        assert Todo.query.filter_by(id=todo.id).first().complete is True

        # Second toggle
        test_client.post(f'/update/{todo.id}', data={})
        assert Todo.query.filter_by(id=todo.id).first().complete is False

class StateTransition_DeleteTaskIrreversibilityTest:

    def test_delete_task_irreversibility(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Delete Forever'))
        todo = Todo.query.filter_by(title='Delete Forever').first()

        # When
        test_client.post(f'/delete/{todo.id}', data={})

        # Then
        assert Todo.query.filter_by(id=todo.id).first() is None

class DomainBoundary_TitleLengthMinTest:

    def test_title_length_min(self, test_client):
        # Given
        response = test_client.post('/add', data=dict(title='A'))

        # When
        new_todo = Todo.query.filter_by(title='A').first()

        # Then
        assert response.status_code == 302
        assert new_todo is not None
        assert new_todo.title == 'A'

class DomainBoundary_TitleLengthMaxTest:

    def test_title_length_max(self, test_client):
        # Given
        long_title = 'A' * 100
        response = test_client.post('/add', data=dict(title=long_title))

        # When
        new_todo = Todo.query.filter_by(title=long_title).first()

        # Then
        assert response.status_code == 302
        assert new_todo is not None
        assert new_todo.title == long_title

class DomainBoundary_TitleLengthBeyondMaxTest:

    def test_title_length_beyond_max(self, test_client):
        # Given
        long_title = 'A' * 101
        response = test_client.post('/add', data=dict(title=long_title))

        # When
        todos = Todo.query.all()

        # Then
        assert response.status_code == 302
        assert all(todo.title != long_title for todo in todos)

class DomainBoundary_UniqueTaskIDTest:

    def test_unique_task_id(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Unique Task 1'))
        test_client.post('/add', data=dict(title='Unique Task 2'))

        # When
        task1 = Todo.query.filter_by(title='Unique Task 1').first()
        task2 = Todo.query.filter_by(title='Unique Task 2').first()

        # Then
        assert task1.id != task2.id

class Security_AddTaskSQLInjectionTest:

    def test_add_task_sql_injection(self, test_client):
        # Given
        malicious_title = "DROP TABLE Todo; --"
        response = test_client.post('/add', data=dict(title=malicious_title))

        # When
        todos = Todo.query.all()

        # Then
        assert response.status_code == 302
        assert all(todo.title != malicious_title for todo in todos)

class Security_AddTaskXSSTest:

    def test_add_task_xss(self, test_client):
        # Given
        xss_title = '<script>alert("XSS")</script>'
        response = test_client.post('/add', data=dict(title=xss_title))

        # When
        todos = Todo.query.all()

        # Then
        assert response.status_code == 302
        assert all(todo.title != xss_title for todo in todos)

class Security_DeleteTaskUnauthorizedTest:

    def test_delete_task_unauthorized(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Unauthorized Task'))
        todo = Todo.query.filter_by(title='Unauthorized Task').first()

        # When
        # Simulate unauthorized deletion attempt
        # Assuming some method to check authorization here
        authorized = False
        if not authorized:
            response = test_client.post(f'/delete/{todo.id}', data={})

        # Then
        assert response.status_code != 302
        assert Todo.query.filter_by(id=todo.id).first() is not None

class Security_DeleteTaskCSRFTest:

    def test_delete_task_csrf(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='CSRF Vulnerable Task'))
        todo = Todo.query.filter_by(title='CSRF Vulnerable Task').first()

        # When
        # Simulate CSRF attempt
        csrf_protected = False
        if not csrf_protected:
            response = test_client.post(f'/delete/{todo.id}', data={})

        # Then
        assert response.status_code != 302
        assert Todo.query.filter_by(id=todo.id).first() is not None

class Failure_CommitFailureOnAddTest:

    def test_commit_failure_on_add(self, test_client):
        # Given
        title = 'Read a book'

        # When
        # Simulate commit failure
        commit_successful = False
        if not commit_successful:
            try:
                test_client.post('/add', data=dict(title=title))
                raise Exception('Simulated database failure')
            except Exception as e:
                db.session.rollback()

        # Then
        todos = Todo.query.all()
        assert all(todo.title != title for todo in todos)

class Failure_CommitFailureOnUpdateTest:

    def test_commit_failure_on_update(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Update Failure Task'))
        todo = Todo.query.filter_by(title='Update Failure Task').first()

        # When
        commit_successful = False
        if not commit_successful:
            try:
                test_client.post(f'/update/{todo.id}', data={})
                raise Exception('Simulated database failure')
            except Exception as e:
                db.session.rollback()

        # Then
        assert Todo.query.filter_by(id=todo.id).first().complete is False

class Failure_CommitFailureOnDeleteTest:

    def test_commit_failure_on_delete(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Delete Failure Task'))
        todo = Todo.query.filter_by(title='Delete Failure Task').first()

        # When
        commit_successful = False
        if not commit_successful:
            try:
                test_client.post(f'/delete/{todo.id}', data={})
                raise Exception('Simulated database failure')
            except Exception as e:
                db.session.rollback()

        # Then
        assert Todo.query.filter_by(id=todo.id).first() is not None

class Recovery_InterruptedAddOperationTest:

    def test_interrupted_add_operation(self, test_client):
        # Given
        title = 'Go jogging'

        # When
        interrupted = True
        if interrupted:
            try:
                test_client.post('/add', data=dict(title=title))
                raise Exception('Simulated interruption')
            except Exception as e:
                db.session.rollback()

        # Then
        todos = Todo.query.all()
        assert all(todo.title != title for todo in todos)

class Recovery_InterruptedUpdateOperationTest:

    def test_interrupted_update_operation(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Update Interrupt Task'))
        todo = Todo.query.filter_by(title='Update Interrupt Task').first()

        # When
        interrupted = True
        if interrupted:
            try:
                test_client.post(f'/update/{todo.id}', data={})
                raise Exception('Simulated interruption')
            except Exception as e:
                db.session.rollback()

        # Then
        assert Todo.query.filter_by(id=todo.id).first().complete is False

class CrossEntity_ConsistencyOnTaskListingTest:

    def test_consistency_on_task_listing(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='Consistency Task 1'))
        test_client.post('/add', data=dict(title='Consistency Task 2'))

        # When
        response = test_client.get('/')

        # Then
        assert response.status_code == 200
        assert b'Consistency Task 1' in response.data
        assert b'Consistency Task 2' in response.data

class CrossEntity_ConsistencyOnTaskStateUpdateTest:

    def test_consistency_on_task_state_update(self, test_client):
        # Given
        test_client.post('/add', data=dict(title='State Update Task'))
        todo = Todo.query.filter_by(title='State Update Task').first()

        # When
        test_client.post(f'/update/{todo.id}', data={})

        # Then
        assert Todo.query.filter_by(id=todo.id).first().complete is True

        # When
        test_client.post(f'/update/{todo.id}', data={})

        # Then
        assert Todo.query.filter_by(id=todo.id).first().complete is False