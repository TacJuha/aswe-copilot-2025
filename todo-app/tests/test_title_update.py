"""Tests for browser title update functionality."""

import pytest
from app.database import Todo


class TestTitleUpdate:
    """Tests for browser tab title updates."""

    def test_create_todo_returns_count_in_oob(self, authenticated_client, test_list):
        """Test that creating a todo returns the updated count in OOB swap."""
        response = authenticated_client.post(
            "/api/todos",
            data={
                "list_id": test_list.id,
                "title": "New Todo",
            },
        )
        assert response.status_code == 200
        # Check that OOB swap for count is present
        assert f'id="list-{test_list.id}-count"'.encode() in response.content
        assert b"hx-swap-oob" in response.content
        # Count should be 1 (the new todo we just created)
        assert b"1</span>" in response.content

    def test_toggle_todo_returns_count_in_oob(self, authenticated_client, test_todo):
        """Test that toggling a todo returns the updated count in OOB swap."""
        response = authenticated_client.patch(
            f"/api/todos/{test_todo.id}/toggle",
        )
        assert response.status_code == 200
        # Check that OOB swap for count is present
        assert f'id="list-{test_todo.list_id}-count"'.encode() in response.content
        assert b"hx-swap-oob" in response.content

    def test_delete_todo_returns_count_in_oob(self, authenticated_client, test_todo, db_session):
        """Test that deleting a todo returns the updated count in OOB swap."""
        list_id = test_todo.list_id
        response = authenticated_client.delete(
            f"/api/todos/{test_todo.id}",
        )
        assert response.status_code == 200
        # Check that OOB swap for count is present
        assert f'id="list-{list_id}-count"'.encode() in response.content
        assert b"hx-swap-oob" in response.content
        # Count should be 0 after deleting the only todo
        assert b"0</span>" in response.content

    def test_multiple_todos_count(self, authenticated_client, test_list, db_session):
        """Test count updates correctly with multiple todos."""
        # Create first todo
        response1 = authenticated_client.post(
            "/api/todos",
            data={"list_id": test_list.id, "title": "Todo 1"},
        )
        assert response1.status_code == 200
        assert b"1</span>" in response1.content

        # Create second todo
        response2 = authenticated_client.post(
            "/api/todos",
            data={"list_id": test_list.id, "title": "Todo 2"},
        )
        assert response2.status_code == 200
        assert b"2</span>" in response2.content

        # Complete first todo - count should decrease to 1
        todos = db_session.query(Todo).filter(Todo.list_id == test_list.id).all()
        first_todo = todos[0]
        response3 = authenticated_client.patch(f"/api/todos/{first_todo.id}/toggle")
        assert response3.status_code == 200
        assert b"1</span>" in response3.content

    def test_title_format_in_template(self, authenticated_client, test_list):
        """Test that the page title block in template has correct format."""
        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200
        # Check that the title is formatted correctly
        assert b"<title>" in response.content
        assert test_list.name.encode() in response.content
        assert b"- Todo App</title>" in response.content
