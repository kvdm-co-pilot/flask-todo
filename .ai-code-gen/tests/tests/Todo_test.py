from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import pytest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title', '')
    if not title:
        return jsonify({'error': 'title cannot be empty'}), 400
    if len(title) > 100:
        return jsonify({'error': 'title is too long'}), 400
    new_todo = Todo(title=title)
    db.session.add(new_todo)
    db.session.commit()
    return redirect('/')

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

class Functional_AddNewTodoItem_WithValidTitleTest:
    def test_add_new_todo_item_with_valid_title(self, test_client):
        # Given
        title = 'Buy groceries'
        response = test_client.post('/add', data=dict(title=title))

        # When
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title=title).first()

        # Then
        assert status_code == 302  # Redirect expected
        assert new_todo is not None
        assert new_todo.title == title

class Functional_AddNewTodoItem_TitleExceedsMaxLengthTest:
    def test_add_new_todo_item_title_exceeds_max_length(self, test_client):
        # Given
        title = 'A very long title that exceeds the maximum length of one hundred characters for to-do items'
        response = test_client.post('/add', data=dict(title=title))

        # When
        status_code = response.status_code
        error_message = response.data.decode()

        # Then
        assert status_code == 400  
        assert 'title is too long' in error_message

class Functional_AddNewTodoItem_WithSpecialCharactersInTitleTest:
    def test_add_new_todo_item_with_special_characters_in_title(self, test_client):
        # Given
        title = 'Meeting @ 5pm! #Important'
        response = test_client.post('/add', data=dict(title=title))

        # When
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title=title).first()

        # Then
        assert status_code == 302  # Redirect expected
        assert new_todo is not None
        assert new_todo.title == title

class Functional_AddNewTodoItem_WithEmptyTitleTest:
    def test_add_new_todo_item_with_empty_title(self, test_client):
        # Given
        title = ''
        response = test_client.post('/add', data=dict(title=title))

        # When
        status_code = response.status_code
        error_message = response.data.decode()

        # Then
        assert status_code == 400
        assert 'title cannot be empty' in error_message

class Functional_AddNewTodoItem_WithDuplicateTitleTest:
    def test_add_new_todo_item_with_duplicate_title(self, test_client):
        # Given
        title = 'Read a book'
        response_first = test_client.post('/add', data=dict(title=title))
        response_second = test_client.post('/add', data=dict(title=title))

        # When
        new_todo_first = Todo.query.filter_by(title=title).first()
        new_todo_second = Todo.query.filter_by(title=title).order_by(Todo.id.desc()).first()

        # Then
        assert response_first.status_code == 302  # Redirect expected
        assert response_second.status_code == 302  # Redirect expected
        assert new_todo_first is not None
        assert new_todo_second is not None
        assert new_todo_first.id != new_todo_second.id

class Invariant_VerifyTodoItemMustHaveTitleTest:
    def test_verify_todo_item_must_have_title(self, test_client):
        # Given
        title = ''
        response = test_client.post('/add', data=dict(title=title))

        # When
        status_code = response.status_code
        error_message = response.data.decode()

        # Then
        assert status_code == 400
        assert 'title cannot be empty' in error_message

class Invariant_VerifyTodoIDMustBeUniqueTest:
    def test_verify_todo_id_must_be_unique(self, test_client):
        # Given
        title = 'Read a book'
        response_first = test_client.post('/add', data=dict(title=title))
        response_second = test_client.post('/add', data=dict(title=title))

        # When
        new_todo_first = Todo.query.filter_by(title=title).first()
        new_todo_second = Todo.query.filter_by(title=title).order_by(Todo.id.desc()).first()

        # Then
        assert response_first.status_code == 302  # Redirect expected
        assert response_second.status_code == 302  # Redirect expected
        assert new_todo_first is not None
        assert new_todo_second is not None
        assert new_todo_first.id != new_todo_second.id

class Boundary_TitleLength_MinValueTest:
    def test_boundary_title_length_min_value(self, test_client):
        # Given
        title = 'A'
        response = test_client.post('/add', data=dict(title=title))

        # When
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title=title).first()

        # Then
        assert status_code == 302  # Redirect expected
        assert new_todo is not None
        assert new_todo.title == title

class Boundary_TitleLength_MaxValueTest:
    def test_boundary_title_length_max_value(self, test_client):
        # Given
        title = 'A' * 100
        response = test_client.post('/add', data=dict(title=title))

        # When
        status_code = response.status_code
        new_todo = Todo.query.filter_by(title=title).first()

        # Then
        assert status_code == 302  # Redirect expected
        assert new_todo is not None
        assert new_todo.title == title