import pytest
from app import app

class App_py_AddTest:
    def setup_method(self):
        self.client = app.test_client()

    def test_add_route_accepts_post_and_returns_success(self):
        data = {"title": "Buy groceries"}
        response = self.client.post("/add", data=data)
        assert response is not None
        assert response.status_code == 200, "Expected HTTP 200 OK from /add POST request"

    def test_add_route_missing_title_still_returns_valid_response(self):
        data = {}
        response = self.client.post("/add", data=data)
        assert response is not None
        assert response.status_code == 200, "Expected graceful handling when title is missing"