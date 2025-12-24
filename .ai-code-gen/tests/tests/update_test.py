from flask import Flask
from app import app as flask_app
from app.models import Todo, db
import pytest

class App_UpdateRouteTest:
    def setup_method(self):
        flask_app.config['TESTING'] = True
        flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        # Initialize the DB within the Flask app context
        with flask_app.app_context():
            db.create_all()
            sample = Todo(id=12, text='Buy groceries')
            db.session.add(sample)
            db.session.commit()

        self.client = flask_app.test_client()

    def teardown_method(self):
        # Drop all tables to clean up between tests
        with flask_app.app_context():
            db.drop_all()

    def test_FUNCTIONAL_UpdateValidTodoItem_ShouldUpdateRecordAndRedirect(self):
        response = self.client.post('/update/12', data={'text': 'Buy groceries and snacks'})

        assert response.status_code in (301, 302)

        # Reload from DB
        with flask_app.app_context():
            updated = Todo.query.filter_by(id=12).first()
            assert updated is not None
            assert updated.text == 'Buy groceries and snacks'
