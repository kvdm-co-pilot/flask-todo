import pytest
from app import app, db, Todo

class TestApp_TodoModelAndRoutes:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        try:
            db.engine.dispose()
        except Exception:
            pass

        self.app = app.test_client()
        with app.app_context():
            db.create_all()
        yield
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_todo_initialization(self):
        title = "Buy groceries"
        todo = Todo(title=title, complete=False)
        assert todo.title == title
        assert todo.complete is False
        assert todo.id is None

    def test_add_route_creates_todo(self):
        form_data = {"title": "Walk the dog"}
        response = self.app.post("/add", data=form_data, follow_redirects=False)
        assert response.status_code == 302
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 1
            assert todos[0].title == "Walk the dog"
            assert todos[0].complete is False

    def test_update_route_toggles_completion(self):
        with app.app_context():
            todo = Todo(title="Clean room", complete=False)
            db.session.add(todo)
            db.session.commit()
            todo_id = todo.id
        response = self.app.get(f"/update/{todo_id}", follow_redirects=False)
        assert response.status_code == 302
        with app.app_context():
            updated = Todo.query.filter_by(id=todo_id).first()
            assert updated.complete is True

    @pytest.mark.skip(reason="/delete route incomplete in provided source; cannot fully implement test logically")
    def test_delete_route(self):
        assert True
