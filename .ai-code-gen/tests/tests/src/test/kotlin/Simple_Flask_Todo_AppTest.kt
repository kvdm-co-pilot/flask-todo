import json
import pytest
from app import app

# Unique test class name derived from the full domain: FlaskTodoEndpoints
class TestFlaskTodoEndpoints:

    @pytest.fixture(autouse=True)
    def setup_client(self):
        # Given: a fresh test client for every test
        self.client = app.test_client()
        # Ensure database starts empty for each test
        with app.app_context():
            from app.models.todo import Todo
            from app import db
            db.drop_all()
            db.create_all()

    def test_functional_create_todo_with_valid_non_empty_title(self):
        # Given
        payload = {"title": "Buy groceries"}

        # When
        response = self.client.post("/todos", json=payload)
        data = response.get_json()

        # Then
        assert response.status_code == 201
        assert data["title"] == "Buy groceries"
        assert data["completed"] is False

    def test_functional_create_todo_trims_leading_trailing_whitespace_successfully(self):
        # Given
        payload = {"title": "   Call mom   "}

        # When
        response = self.client.post("/todos", json=payload)
        data = response.get_json()

        # Then
        assert response.status_code == 201
        assert data["title"] == "Call mom"

    def test_functional_create_todo_rejects_whitespace_only_title(self):
        # Given
        payload = {"title": "   "}

        # When
        response = self.client.post("/todos", json=payload)

        # Then
        assert response.status_code == 400

    def test_functional_create_todo_persists_default_not_completed_status(self):
        # Given
        payload = {"title": "Wash car"}

        # When
        response = self.client.post("/todos", json=payload)
        data = response.get_json()

        # Then
        assert response.status_code == 201
        assert data["completed"] is False

    def test_functional_get_todos_returns_all_persisted_todos(self):
        # Given
        self.client.post("/todos", json={"title": "Buy milk"})
        self.client.post("/todos", json={"title": "Read book"})

        # When
        response = self.client.get("/todos")
        data = response.get_json()

        # Then
        assert response.status_code == 200
        assert len(data) == 2
        assert data[0]["title"] == "Buy milk"
        assert data[1]["title"] == "Read book"

    def test_functional_get_todos_ordering_consistent_by_primary_key(self):
        # Given
        self.client.post("/todos", json={"title": "A"})
        self.client.post("/todos", json={"title": "B"})
        self.client.post("/todos", json={"title": "C"})

        # When
        response = self.client.get("/todos")
        data = response.get_json()

        # Then
        assert response.status_code == 200
        ids = [t["id"] for t in data]
        assert ids == sorted(ids)

    def test_functional_complete_todo_transitions_status_to_completed(self):
        # Given
        created = self.client.post("/todos", json={"title": "Do laundry"}).get_json()
        todo_id = created["id"]

        # When
        response = self.client.post(f"/todos/{todo_id}/complete")
        data = response.get_json()

        # Then
        assert response.status_code == 200
        assert data["completed"] is True

    def test_functional_complete_todo_idempotent_no_change_when_already_completed(self):
        # Given
        created = self.client.post("/todos", json={"title": "Jogging"}).get_json()
        todo_id = created["id"]
        self.client.post(f"/todos/{todo_id}/complete")  # First completion

        # When
        response = self.client.post(f"/todos/{todo_id}/complete")
        data = response.get_json()

        # Then
        assert response.status_code == 200
        assert data["completed"] is True

    def test_functional_complete_todo_non_existent_id_returns_404(self):
        # Given: nonexistent id 9999

        # When
        response = self.client.post("/todos/9999/complete")

        # Then
        assert response.status_code == 404

    def test_functional_delete_todo_removes_row_from_sqlite(self):
        # Given
        created = self.client.post("/todos", json={"title": "Trash"}).get_json()
        todo_id = created["id"]

        # When
        response = self.client.delete(f"/todos/{todo_id}")

        # Then
        assert response.status_code == 204
        remaining = self.client.get("/todos").get_json()
        assert all(t["id"] != todo_id for t in remaining)

    def test_functional_delete_todo_non_existent_id_returns_404_no_change(self):
        # Given
        self.client.post("/todos", json={"title": "One"})

        # When
        response = self.client.delete("/todos/888")
        remaining = self.client.get("/todos").get_json()

        # Then
        assert response.status_code == 404
        assert len(remaining) == 1

    def test_functional_prevent_duplicate_title_when_uniqueness_rule_enabled(self):
        # Given
        self.client.post("/todos", json={"title": "Pay bills"})

        # When
        response = self.client.post("/todos", json={"title": "Pay bills"})

        # Then
        assert response.status_code in (400, 409)

    def test_functional_allow_duplicate_title_when_uniqueness_rule_disabled(self):
        # Given
        # Assuming policy disabled is simulated by allowing duplicates
        self.client.post("/todos", json={"title": "Walk dog"})
        response2 = self.client.post("/todos", json={"title": "Walk dog"})

        # Then
        assert response2.status_code == 201
        todos = self.client.get("/todos").get_json()
        assert len([t for t in todos if t["title"] == "Walk dog"]) == 2

    def test_functional_title_boundary_at_max_length_accepted(self):
        # Given
        max_title = "A" * 255
        payload = {"title": max_title}

        # When
        response = self.client.post("/todos", json=payload)
        data = response.get_json()

        # Then
        assert response.status_code == 201
        assert data["title"] == max_title

    def test_functional_title_boundary_exceeds_max_length_rejected_or_truncated(self):
        # Given
        too_long = "A" * 256
        payload = {"title": too_long}

        # When
        response = self.client.post("/todos", json=payload)

        # Then
        assert response.status_code in (400, 413)

    def test_functional_handle_malformed_post_missing_title_field_returns_400(self):
        # Given
        payload = {}

        # When
        response = self.client.post("/todos", json=payload)

        # Then
        assert response.status_code == 400

    def test_functional_handle_malformed_post_invalid_json_returns_400(self):
        # Given invalid raw body
        bad_body = ":::badjson"

        # When
        response = self.client.post("/todos", data=bad_body, content_type="application/json")

        # Then
        assert response.status_code == 400
