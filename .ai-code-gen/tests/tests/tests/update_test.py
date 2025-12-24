import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Todo
from app import app as flask_app, db

class UpdateRouteTest:
    @pytest.fixture
    def session(self):
        engine = create_engine("sqlite:///:memory:")
        Todo.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        s = Session()
        try:
            yield s
        finally:
            s.close()

    @pytest.fixture
    def client(self):
        flask_app.config["TESTING"] = True
        with flask_app.test_client() as c:
            yield c

    def test_exact_functional_update_valid_todo_updates_item_and_redirects_home(self, session, client, monkeypatch):
        todo = Todo(title="Old Title")
        session.add(todo)
        session.commit()

        # Patch db.session used by app so it uses our session's methods
        monkeypatch.setattr(db, "session", session)

        response = client.post(f"/update/{todo.id}", data={"title": "Buy eggs"})

        assert response.status_code in (301, 302)
        updated = session.query(Todo).filter_by(id=todo.id).first()
        assert updated is not None
        assert updated.title == "Buy eggs"