import pytest
from app import Todo

class TestApp_TodoModel:
    def setup_method(self):
        self.sample_title = "Buy groceries and supplies"

    def test_todo_initialization_sets_title_and_default_id_none(self):
        title = self.sample_title
        todo = Todo(title=title)
        assert todo.title == title
        assert todo.id is None

    def test_todo_allows_different_realistic_titles(self):
        title = "Schedule annual medical checkup"
        todo = Todo(title=title)
        assert todo.title == title
        assert todo.id is None

    def test_todo_title_assignment_independence_between_instances(self):
        title1 = "Complete tax documents"
        title2 = "Call the electrician"
        todo1 = Todo(title=title1)
        todo2 = Todo(title=title2)
        assert todo1.title == title1
        assert todo2.title == title2
        assert todo1.title != todo2.title
        assert todo1.id is None
        assert todo2.id is None"
}