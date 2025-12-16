# test_app_add_task.py

# Import statements
import pytest
from app import app, db
from flask import url_for

# Test class name derived from entity path
class TestAppAddTask:
    @pytest.fixture(scope='module')
    def test_client(self):
        # Given
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.test_client() as testing_client:
            with app.app_context():
                db.create_all()
                yield testing_client
                db.drop_all()

    def test_add_valid_task(self, test_client):
        # Given
        valid_task_data = {'title': 'Buy groceries'}

        # When
        response = test_client.post('/add', data=valid_task_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Buy groceries' in response.data

    def test_add_empty_task_title(self, test_client):
        # Given
        empty_title_data = {'title': ''}

        # When
        response = test_client.post('/add', data=empty_title_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Task title cannot be empty' in response.data

    def test_add_task_exceeding_character_limit(self, test_client):
        # Given
        long_title_data = {'title': 'a'*101}

        # When
        response = test_client.post('/add', data=long_title_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Task title exceeds character limit' in response.data

    def test_add_task_with_special_characters(self, test_client):
        # Given
        special_char_title_data = {'title': 'Buy groceries @ 6pm!'}

        # When
        response = test_client.post('/add', data=special_char_title_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'Buy groceries @ 6pm!' in response.data

    def test_add_task_to_full_list(self, test_client):
        # Setup: Fill the list with 50 tasks
        for i in range(50):
            test_client.post('/add', data={'title': f'Task {i}'}, follow_redirects=True)

        # Given
        full_list_data = {'title': 'Book Flight'}

        # When
        response = test_client.post('/add', data=full_list_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'ToDo List is full' in response.data

    def test_unique_todo_id(self, test_client):
        # Given
        first_task_data = {'title': 'First Task'}
        second_task_data = {'title': 'Second Task'}

        # When
        test_client.post('/add', data=first_task_data, follow_redirects=True)
        test_client.post('/add', data=second_task_data, follow_redirects=True)

        # Then
        first_task = db.session.query(Todo).filter_by(title='First Task').first()
        second_task = db.session.query(Todo).filter_by(title='Second Task').first()
        assert first_task.id != second_task.id

    def test_task_title_length_limit(self, test_client):
        # Given
        valid_title_data = {'title': 'A'*100}
        invalid_title_data = {'title': 'B'*101}

        # When
        valid_response = test_client.post('/add', data=valid_title_data, follow_redirects=True)
        invalid_response = test_client.post('/add', data=invalid_title_data, follow_redirects=True)

        # Then
        assert valid_response.status_code == 200
        assert invalid_response.status_code == 400
        assert b'Task title exceeds character limit' in invalid_response.data

    def test_add_new_task_state_transition(self, test_client):
        # Given
        new_task_data = {'title': 'New Task'}

        # When
        response = test_client.post('/add', data=new_task_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'New Task' in response.data

    def test_toggle_task_completion_status(self, test_client):
        # Setup: Add a task
        test_client.post('/add', data={'title': 'Toggle Task'}, follow_redirects=True)

        # Given
        task_to_toggle = db.session.query(Todo).filter_by(title='Toggle Task').first()

        # When
        response = test_client.get(f'/update/{task_to_toggle.id}', follow_redirects=True)

        # Then
        updated_task = db.session.query(Todo).filter_by(id=task_to_toggle.id).first()
        assert updated_task.complete is True
        assert response.status_code == 200

    def test_deletion_of_task_state_transition(self, test_client):
        # Setup: Add a task
        test_client.post('/add', data={'title': 'Delete Task'}, follow_redirects=True)

        # Given
        task_to_delete = db.session.query(Todo).filter_by(title='Delete Task').first()

        # When
        response = test_client.get(f'/delete/{task_to_delete.id}', follow_redirects=True)

        # Then
        deleted_task = db.session.query(Todo).filter_by(id=task_to_delete.id).first()
        assert deleted_task is None
        assert response.status_code == 200

    def test_boundary_task_title_length_min(self, test_client):
        # Given
        min_length_title_data = {'title': 'A'}

        # When
        response = test_client.post('/add', data=min_length_title_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'A' in response.data

    def test_boundary_task_title_length_max(self, test_client):
        # Given
        max_length_title_data = {'title': 'B'*100}

        # When
        response = test_client.post('/add', data=max_length_title_data, follow_redirects=True)

        # Then
        assert response.status_code == 200
        assert b'B'*100 in response.data

    def test_boundary_task_title_length_empty_string(self, test_client):
        # Given
        empty_title_data = {'title': ''}

        # When
        response = test_client.post('/add', data=empty_title_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Task title cannot be empty' in response.data

    def test_boundary_task_completion_status_toggle(self, test_client):
        # Setup: Add and toggle task completion status
        test_client.post('/add', data={'title': 'Toggle Task'}, follow_redirects=True)
        task_to_toggle = db.session.query(Todo).filter_by(title='Toggle Task').first()

        # When
        test_client.get(f'/update/{task_to_toggle.id}', follow_redirects=True)

        # Then
        toggled_task = db.session.query(Todo).filter_by(id=task_to_toggle.id).first()
        assert toggled_task.complete is True

        # When
        test_client.get(f'/update/{task_to_toggle.id}', follow_redirects=True)

        # Then
        toggled_task = db.session.query(Todo).filter_by(id=task_to_toggle.id).first()
        assert toggled_task.complete is False

    def test_security_add_task_sql_injection(self, test_client):
        # Given
        sql_injection_data = {'title': "'; DROP TABLE tasks;--"}

        # When
        response = test_client.post('/add', data=sql_injection_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Invalid task title' in response.data

    def test_security_add_task_xss(self, test_client):
        # Given
        xss_data = {'title': '<script>alert("XSS")</script>'}

        # When
        response = test_client.post('/add', data=xss_data, follow_redirects=True)

        # Then
        assert response.status_code == 400
        assert b'Invalid task title' in response.data

    def test_security_delete_task_csrf(self, test_client):
        # Given
        test_client.post('/add', data={'title': 'CSRF Task'}, follow_redirects=True)
        task_to_delete = db.session.query(Todo).filter_by(title='CSRF Task').first()

        # When
        response = test_client.post(f'/delete/{task_to_delete.id}', headers={'Referer': 'http://malicious-site.com'}, follow_redirects=True)

        # Then
        assert response.status_code == 403
        assert b'CSRF protection triggered' in response.data

    def test_security_delete_task_broken_authentication(self, test_client):
        # Given
        test_client.post('/add', data={'title': 'Auth Task'}, follow_redirects=True)
        task_to_delete = db.session.query(Todo).filter_by(title='Auth Task').first()

        # When
        response = test_client.get(f'/delete/{task_to_delete.id}', headers={'Authorization': 'InvalidToken'}, follow_redirects=True)

        # Then
        assert response.status_code == 401
        assert b'Unauthorized access' in response.data

    def test_failure_add_task_database_write_failure(self, test_client):
        # Simulate database failure
        db.session.commit = lambda: (_ for _ in ()).throw(Exception("Database write failure"))

        # Given
        db_failure_data = {'title': 'DB Failure Task'}

        # When
        response = test_client.post('/add', data=db_failure_data, follow_redirects=True)

        # Then
        assert response.status_code == 500
        assert b'Database write error' in response.data

    def test_failure_add_task_network_issue(self, test_client):
        # Simulate network issue
        app.test_client = lambda: (_ for _ in ()).throw(Exception("Network issue"))

        # Given
        network_issue_data = {'title': 'Network Issue Task'}

        # When
        response = test_client.post('/add', data=network_issue_data, follow_redirects=True)

        # Then
        assert response.status_code == 503
        assert b'Network issue, please try again' in response.data

    def test_failure_delete_task_database_delete_failure(self, test_client):
        # Simulate database failure
        db.session.delete = lambda _: (_ for _ in ()).throw(Exception("Database delete failure"))

        # Given
        test_client.post('/add', data={'title': 'Delete Failure Task'}, follow_redirects=True)
        task_to_delete = db.session.query(Todo).filter_by(title='Delete Failure Task').first()

        # When
        response = test_client.get(f'/delete/{task_to_delete.id}', follow_redirects=True)

        # Then
        assert response.status_code == 500
        assert b'Unable to delete task, please try again later' in response.data

    def test_failure_delete_task_network_issue(self, test_client):
        # Simulate network issue
        app.test_client = lambda: (_ for _ in ()).throw(Exception("Network issue"))

        # Given
        test_client.post('/add', data={'title': 'Network Issue Delete Task'}, follow_redirects=True)
        task_to_delete = db.session.query(Todo).filter_by(title='Network Issue Delete Task').first()

        # When
        response = test_client.get(f'/delete/{task_to_delete.id}', follow_redirects=True)

        # Then
        assert response.status_code == 503
        assert b'Network issue, please try again' in response.data

    def test_consistency_task_list_retrieval(self, test_client):
        # Given
        task_titles = ['Task1', 'Task2', 'Task3']
        for title in task_titles:
            test_client.post('/add', data={'title': title}, follow_redirects=True)

        # When
        response = test_client.get('/', follow_redirects=True)

        # Then
        for title in task_titles:
            assert title.encode() in response.data

    def test_consistency_task_list_after_add(self, test_client):
        # Given
        add_task_data = {'title': 'Immediate Add Task'}

        # When
        response = test_client.post('/add', data=add_task_data, follow_redirects=True)

        # Then
        assert b'Immediate Add Task' in response.data

    def test_consistency_task_list_after_delete(self, test_client):
        # Setup: Add a task
        test_client.post('/add', data={'title': 'Immediate Delete Task'}, follow_redirects=True)
        task_to_delete = db.session.query(Todo).filter_by(title='Immediate Delete Task').first()

        # When
        response = test_client.get(f'/delete/{task_to_delete.id}', follow_redirects=True)

        # Then
        assert b'Immediate Delete Task' not in response.data
