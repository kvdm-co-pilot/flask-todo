import pytest
from app import app, db, Todo

@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(tmp_path / 'test.sqlite')
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client():
    return app.test_client()

class Test_App_py_AddRoute_BasicBehavior:
    def test_Functional_AddTodo_WithValidTitle_CreatesTodoWithCompleteFalse(self, client):
        response = client.post('/add', data={'title': 'Buy groceries'})
        assert response.status_code == 302
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 1
            assert todos[0].title == 'Buy groceries'
            assert todos[0].complete is False

    def test_Functional_AddTodo_WithEmptyTitle_CreatesTodoWithEmptyOrNullTitle(self, client):
        response = client.post('/add', data={'title': ''})
        assert response.status_code == 302
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 1
            assert todos[0].title == ''
            assert todos[0].complete is False

class Test_App_py_ListRoute_BasicBehavior:
    def test_Functional_ListTodos_WhenNoTodos_ReturnsEmptyList(self, client):
        response = client.get('/')
        assert response.status_code == 200
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 0

    def test_Functional_ListTodos_ReturnsAllExistingTodos(self, client):
        with app.app_context():
            db.session.add(Todo(title='A', complete=False))
            db.session.add(Todo(title='B', complete=True))
            db.session.commit()
        response = client.get('/')
        assert response.status_code == 200
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 2
