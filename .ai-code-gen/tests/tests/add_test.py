# test_add_task.py

import pytest
from app import create_app, db
from app.models import Todo
from flask import request

class TestAddTask:
    def setup_method(self):
        """Setup test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def teardown_method(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_task_with_valid_title(self):
        """Test adding a task with a valid title"""
        response = self.client.post('/add', data={'title': 'Buy groceries'})
        assert response.status_code == 200
        assert b'Buy groceries' in response.data

    def test_add_task_with_empty_title_should_display_error(self):
        """Test adding a task with an empty title displays error"""
        response = self.client.post('/add', data={'title': ''})
        assert response.status_code == 400
        assert b'Title is required' in response.data

    def test_add_task_with_exceeding_character_limit_should_display_error(self):
        """Test adding a task with a title exceeding 100 characters"""
        long_title = 'x' * 101
        response = self.client.post('/add', data={'title': long_title})
        assert response.status_code == 400
        assert b'Title is too long' in response.data

    def test_add_task_with_special_characters_valid_characters_allowed(self):
        """Test adding a task with special characters in title"""
        response = self.client.post('/add', data={'title': 'Review PR #123!'})
        assert response.status_code == 200
        assert b'Review PR #123!' in response.data

    def test_add_duplicate_task_title_allows_separate_entry(self):
        """Test adding duplicate task titles as separate entries"""
        response1 = self.client.post('/add', data={'title': 'Buy groceries'})
        response2 = self.client.post('/add', data={'title': 'Buy groceries'})
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_security_add_task_sql_injection_prevent_injection(self):
        """Test SQL injection vulnerability when adding a task"""
        response = self.client.post('/add', data={'title': "1; DROP TABLE tasks;--"})
        assert response.status_code == 400
        assert b'Invalid title' in response.data

    def test_security_add_task_cross_site_scripting_prevent_xss(self):
        """Test XSS vulnerability when adding a task with malicious input"""
        response = self.client.post('/add', data={'title': "<script>alert('XSS')</script>"})
        assert response.status_code == 400
        assert b'Invalid title' in response.data

    def test_failure_recovery_add_task_database_connection_failure_should_display_error(self):
        """Test database connection failure when adding task"""
        # Simulate database down
        self.app.config['DATABASE_STATUS'] = 'down'
        response = self.client.post('/add', data={'title': 'New Task'})
        assert response.status_code == 500
        assert b'Database connection issue' in response.data

    def test_cross_entity_consistency_task_id_mapping_verify_unique_and_correct_mapping(self):
        """Test task IDs are unique and correctly mapped"""
        with self.app.app_context():
            task1 = Todo(id='1', title='Task A')
            task2 = Todo(id='2', title='Task B')
            db.session.add(task1)
            db.session.add(task2)
            db.session.commit()
            task_list = Todo.query.all()
            assert len(task_list) == 2
            assert task_list[0].id != task_list[1].id
