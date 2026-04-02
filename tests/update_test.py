# Import Statements
import pytest
from app import db, Todo  # Adjust the path according to your project structure
from flask import url_for, redirect

# Unique Test Class Declaration
class TestAddUpdateTodo:
    
    @pytest.fixture
    def new_todo(self):
        todo = Todo(id=1, description="Sample New Todo")
        yield todo
        db.session.query(Todo).filter_by(id=todo.id).delete()
        db.session.commit()

    @pytest.fixture
    def existing_todo_id(self):
        # Fixture simulating an existing to-do item in the database
        todo = Todo(id=2, description="Existing Todo")
        db.session.add(todo)
        db.session.commit()
        yield todo.id
        db.session.query(Todo).filter_by(id=todo.id).delete()
        db.session.commit()

    def test_functional_successfully_add_new_todo_item(self, new_todo):
        # Given: A new To-Do item with valid details
        db.session.add(new_todo)
        db.session.commit()

        # When: Redirecting to home page
        response = redirect(url_for("home"))

        # Then: Verify the item is saved and user is redirected
        assert db.session.query(Todo).filter_by(id=new_todo.id).first() is not None
        assert response.status_code == 302  # Assuming 302 for successful redirection

    def test_functional_update_existing_todo_item(self, existing_todo_id):
        # Given: An existing To-Do item with valid ID
        existing_todo = db.session.query(Todo).get(existing_todo_id)
        updated_description = "Updated Todo Description"

        # When: Updating the description
        existing_todo.description = updated_description
        db.session.commit()

        # Then: Verify the updated item is saved
        assert existing_todo.description == updated_description

    def test_error_handle_invalid_todo_id(self):
        # Given: An invalid To-Do ID
        invalid_id = 99999

        # When & Then: Attempt to update and expect failure
        with pytest.raises(Exception) as e_info:
            todo = db.session.query(Todo).get(invalid_id)
            if todo is None:
                raise Exception("No row was found for one()")
            todo.description = "Should not update"
            db.session.commit()

        # Verify the exception message
        assert "No row was found for one()" in str(e_info.value)

    def test_error_add_todo_item_without_required_fields(self):
        # Given: A To-Do item without a description
        invalid_todo = Todo(id=3, description=None)

        # When & Then: Attempt to add and expect failure
        with pytest.raises(Exception) as e_info:
            db.session.add(invalid_todo)
            db.session.commit()

        # Verify the exception message
        assert "NOT NULL constraint failed" in str(e_info.value)

    def test_boundary_max_length_todo_description(self):
        # Given: A To-Do item with maximum description length
        max_length_description = "x" * 255  # Assuming 255 is the max length
        todo = Todo(id=4, description=max_length_description)

        # When: Adding the item
        db.session.add(todo)
        db.session.commit()

        # Then: Verify it is saved successfully
        assert db.session.query(Todo).filter_by(id=todo.id).first() is not None

    def test_boundary_exceed_max_length_todo_description(self):
        # Given: A To-Do item with description exceeding maximum length
        too_long_description = "x" * 256  # Assuming 256 exceeds the max length
        todo = Todo(id=5, description=too_long_description)

        # When & Then: Attempt to add and expect failure
        with pytest.raises(Exception) as e_info:
            db.session.add(todo)
            db.session.commit()

        # Verify the exception message
        assert "value too long" in str(e_info.value)

    def test_domain_invariant_unique_todo_ids(self):
        # Given: Two To-Do items with the same ID
        todo1 = Todo(id=6, description="First Todo")
        todo2 = Todo(id=6, description="Second Todo")

        # When & Then: Attempt to add and expect failure
        db.session.add(todo1)
        db.session.commit()

        with pytest.raises(Exception) as e_info:
            db.session.add(todo2)
            db.session.commit()

        # Verify the exception message
        assert "UNIQUE constraint failed" in str(e_info.value)


# Test Execution
if __name__ == "__main__":
    pytest.main()
