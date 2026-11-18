from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.auth.schemas import Token
from src.todo.models import ToDo
from src.todo.schemas import PaginatedTodos


class TestToken:
    """Tests for the Token schema."""

    def test_default_token_type(self) -> None:
        """Test that token_type defaults to bearer."""
        token = Token(access_token="abc")

        assert token.access_token == "abc"
        assert token.token_type == "bearer"

    def test_explicit_token_type(self) -> None:
        """Test overriding token_type."""
        assert Token(access_token="abc", token_type="mac").token_type == "mac"

    def test_access_token_required(self) -> None:
        """Test that access_token is required."""
        with pytest.raises(ValidationError):
            Token()  # pyrefly: ignore[missing-argument]

    def test_dump(self) -> None:
        """Test serialization."""
        assert Token(access_token="abc").model_dump() == {"access_token": "abc", "token_type": "bearer"}


class TestPaginatedTodos:
    """Tests for the PaginatedTodos schema."""

    def test_empty(self) -> None:
        """Test an empty page."""
        page = PaginatedTodos(total=0, items=[])

        assert page.total == 0
        assert page.items == []

    def test_with_items(self) -> None:
        """Test a page holding ToDo instances."""
        uid = uuid4()
        items = [ToDo(title=f"t{i}", priority=i, user_id=uid) for i in range(3)]
        page = PaginatedTodos(total=10, items=items)

        assert page.total == 10
        assert [item.title for item in page.items] == ["t0", "t1", "t2"]

    def test_serialization_with_items(self) -> None:
        """Test that items serialize with stringified UUIDs in JSON mode."""
        uid = uuid4()
        todo = ToDo(title="t", priority=1, user_id=uid)
        data = PaginatedTodos(total=1, items=[todo]).model_dump(mode="json")

        assert data["total"] == 1
        assert data["items"][0]["id"] == str(todo.id)
        assert data["items"][0]["user_id"] == str(uid)

    def test_items_from_dicts(self) -> None:
        """Test validating dict items into ToDo models (table models do not coerce field types)."""
        uid = uuid4()
        payload = {"total": 1, "items": [{"title": "t", "priority": 1, "user_id": str(uid)}]}
        page = PaginatedTodos.model_validate(payload)

        assert isinstance(page.items[0], ToDo)
        assert page.items[0].title == "t"
        # Table models skip validation, so the string user_id is not coerced to UUID.
        assert page.items[0].user_id == str(uid)  # pyrefly: ignore[bad-argument-type]

    @pytest.mark.parametrize("total", ["abc", None, 1.5])
    def test_invalid_total(self, total: object) -> None:
        """Test that a non-integer total fails."""
        with pytest.raises(ValidationError):
            PaginatedTodos(total=total, items=[])  # pyrefly: ignore[bad-argument-type]

    def test_total_coercion(self) -> None:
        """Test that a numeric string total is coerced."""
        assert PaginatedTodos(total="4", items=[]).total == 4  # pyrefly: ignore[bad-argument-type]

    def test_invalid_item(self) -> None:
        """Test that a non-ToDo item fails."""
        with pytest.raises(ValidationError):
            PaginatedTodos(total=1, items=["nope"])  # pyrefly: ignore[bad-argument-type]

    def test_missing_fields(self) -> None:
        """Test that total and items are required."""
        with pytest.raises(ValidationError) as exc_info:
            PaginatedTodos()  # pyrefly: ignore[missing-argument]

        assert {str(e["loc"][0]) for e in exc_info.value.errors()} == {"total", "items"}
