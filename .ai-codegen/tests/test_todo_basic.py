import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

# create_valid_todo
def test_todo_create_valid_todo(client):
    with app.app_context():
        t = Todo(title='Test', complete=False)
        db.session.add(t)
        db.session.commit()
        assert t.id is not None
        assert t.title == 'Test'
        assert t.complete is False

# add_valid_todo
def test_add_route_add_valid_todo(client):
    resp = client.post('/add', data={'title': 'Buy milk'})
    assert resp.status_code == 302
    with app.app_context():
        todos = Todo.query.all()
        assert len(todos) == 1
        assert todos[0].title == 'Buy milk'

# delete_existing_todo
def test_delete_existing_todo(client):
    with app.app_context():
        t = Todo(title='X', complete=False)
        db.session.add(t)
        db.session.commit()
        tid = t.id
    resp = client.get(f'/delete/{tid}')
    assert resp.status_code == 302
    with app.app_context():
        assert Todo.query.get(tid) is None

# toggle_existing_todo
def test_update_toggle_existing_todo(client):
    with app.app_context():
        t = Todo(title='Y', complete=False)
        db.session.add(t)
        db.session.commit()
        tid = t.id
    client.get(f'/update/{tid}')
    with app.app_context():
        updated = Todo.query.get(tid)
        assert updated.complete is True

# home_no_todos
def test_home_no_todos(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"" in resp.data

# form_urlencoded_submission
def test_form_urlencoded_submission(client):
    resp = client.post('/add', data={'title': 'New Item'})
    assert resp.status_code == 302
    with app.app_context():
        assert Todo.query.filter_by(title='New Item').first() is not None
