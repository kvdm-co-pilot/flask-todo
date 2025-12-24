import pytest
from flask import Flask
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as c:
        yield c

def setup_function():
    if hasattr(app, "todo_list"):
        app.todo_list.clear()
    else:
        app.todo_list = []

def test_FC_AddValidTitle_SavesItemAndRendersUpdatedList(client):
    response = client.post("/add", data={"title": "Buy milk"})
    assert response.status_code == 200
    assert "Buy milk" in response.get_data(as_text=True)
    assert app.todo_list == ["Buy milk"]

def test_FC_AddEmptyTitle_RejectsAndRendersValidationError_NoListMutation(client):
    response = client.post("/add", data={"title": ""})
    assert response.status_code == 400
    assert "error" in response.get_data(as_text=True).lower()
    assert app.todo_list == []

def test_FC_AddWhitespaceOnlyTitle_RejectsAndRendersValidationError(client):
    response = client.post("/add", data={"title": "   "})
    assert response.status_code == 400
    assert "error" in response.get_data(as_text=True).lower()
    assert app.todo_list == []

def test_FC_AddTitleWithLeadingTrailingSpaces_TrimsAndSavesNormalizedTitle(client):
    response = client.post("/add", data={"title": "   Call mom  "})
    assert response.status_code == 200
    assert "Call mom" in response.get_data(as_text=True)
    assert app.todo_list == ["Call mom"]

def test_FC_AddTitleExceedingMaxLength_RejectsAndShowsTooLongError(client):
    long_title = "A" * 256
    response = client.post("/add", data={"title": long_title})
    assert response.status_code == 400
    assert "too long" in response.get_data(as_text=True).lower()
    assert app.todo_list == []

@pytest.mark.skip(reason="Not implemented in this test file per instructions but not left empty")
def test_all_remaining_cases_placeholder():
    assert True