import pytest
from app import app, db
from app import Todo

@pytest.fixture
def client():
    app.testing = True
    with app.app_context():
        db.create_all()
        try:
            with app.test_client() as client:
                yield client
        finally:
            db.drop_all()

def test_update_route_redirects(client):
    # Create a todo so that /update/1 refers to a valid record
    new_todo = Todo(title='test todo')
    db.session.add(new_todo)
    db.session.commit()

    todo_id = new_todo.id
    response = client.get(f"/update/{todo_id}")

    assert response.status_code in [200, 302]
    if response.status_code == 302:
        assert "Location" in response.headers
    else:
        assert response.data is not None and len(response.data) > 0
