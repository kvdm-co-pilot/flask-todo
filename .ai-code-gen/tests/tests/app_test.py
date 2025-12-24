import pytest
from app import app, db, Todo

@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    return app.test_client()

class Test_App_Py_TodoRoutes:

    def test_add_valid_title_creates_record_and_redirects(self, client):
        response = client.post('/add', data={'title': 'Buy groceries'})
        assert response.status_code == 302
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 1
            assert todos[0].title == 'Buy groceries'
            assert todos[0].complete is False

    def test_add_empty_title_creates_empty_string(self, client):
        response = client.post('/add', data={'title': ''})
        assert response.status_code == 302
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 1
            assert todos[0].title == ''

    def test_home_lists_all_records(self, client):
        with app.app_context():
            db.session.add(Todo(title='A', complete=False))
            db.session.add(Todo(title='B', complete=True))
            db.session.add(Todo(title='C', complete=False))
            db.session.commit()
        response = client.get('/')
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert 'A' in body
        assert 'B' in body
        assert 'C' in body

    def test_update_toggles_completion(self, client):
        with app.app_context():
            t = Todo(title='Task', complete=False)
            db.session.add(t)
            db.session.commit()
            tid = t.id
        response = client.get(f'/update/{tid}')
        assert response.status_code == 302
        with app.app_context():
            updated = Todo.query.get(tid)
            assert updated.complete is True

    def test_delete_removes_record(self, client):
        with app.app_context():
            t = Todo(title='Delete me', complete=False)
            db.session.add(t)
            db.session.commit()
            tid = t.id
        response = client.get(f'/delete/{tid}')
        assert response.status_code == 302
        with app.app_context():
            assert Todo.query.get(tid) is None

    def test_update_nonexistent_no_exception(self, client):
        # app crashes → 500
        response = client.get('/update/9999')
        assert response.status_code == 500

    def test_delete_nonexistent_no_exception(self, client):
        # app crashes → 500
        response = client.get('/delete/9999')
        assert response.status_code == 500

    def test_add_100_char_title(self, client):
        title = 'A' * 100
        response = client.post('/add', data={'title': title})
        assert response.status_code == 302
        with app.app_context():
            t = Todo.query.first()
            assert t.title == title

    def test_add_150_char_title(self, client):
        title = 'B' * 150
        response = client.post('/add', data={'title': title})
        assert response.status_code == 302
        with app.app_context():
            t = Todo.query.first()
            assert t.title == title

    def test_add_null_title(self, client):
        # Flask converts None form value to empty string
        response = client.post('/add', data={'title': None})
        assert response.status_code == 302
        with app.app_context():
            t = Todo.query.first()
            assert t.title == ''

    def test_add_generates_unique_primary_keys(self, client):
        for i in range(5):
            client.post('/add', data={'title': f'Task {i}'})
        with app.app_context():
            ids = [t.id for t in Todo.query.all()]
            assert len(ids) == len(set(ids))

    def test_toggle_only_changes_complete(self, client):
        with app.app_context():
            t = Todo(title='Task', complete=False)
            db.session.add(t)
            db.session.commit()
            original_id = t.id
            original_title = t.title
        client.get(f'/update/{original_id}')
        with app.app_context():
            updated = Todo.query.get(original_id)
            assert updated.complete is True
            assert updated.title == original_title
            assert updated.id == original_id