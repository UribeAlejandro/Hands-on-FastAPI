from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.todo.models import ToDo, ToDoBase, ToDoCreate, ToDoUpdate


def error_locs(exc_info: pytest.ExceptionInfo[ValidationError]) -> set[str]:
    """Return the set of field names that failed validation."""
    return {str(err["loc"][0]) for err in exc_info.value.errors()}


class TestToDoBase:
    """Tests for ToDoBase validation."""

    def test_valid_with_defaults(self) -> None:
        """Test valid construction and defaults."""
        todo = ToDoBase(title="Write tests", priority=1)

        assert todo.title == "Write tests"
        assert todo.description is None
        assert todo.completed is False

    def test_all_fields(self) -> None:
        """Test construction with every field."""
        todo = ToDoBase(title="t", description="d", priority=3, completed=True)

        assert todo.model_dump() == {"title": "t", "description": "d", "priority": 3, "completed": True}

    @pytest.mark.parametrize("field", ["title", "priority"])
    def test_missing_required(self, field: str) -> None:
        """Test that title and priority are required."""
        payload: dict[str, Any] = {"title": "t", "priority": 1}
        del payload[field]

        with pytest.raises(ValidationError) as exc_info:
            ToDoBase(**payload)

        assert error_locs(exc_info) == {field}

    @pytest.mark.parametrize(("value", "expected"), [("5", 5), (5, 5), (5.0, 5), (-1, -1), (0, 0)])
    def test_priority_coercion(self, value: Any, expected: int) -> None:
        """Test lax coercion of priority to int; no range constraint exists."""
        assert ToDoBase(title="t", priority=value).priority == expected

    @pytest.mark.parametrize("value", ["abc", "", 5.5, None, [1]])
    def test_priority_invalid(self, value: Any) -> None:
        """Test that non-integer priorities fail."""
        with pytest.raises(ValidationError) as exc_info:
            ToDoBase(title="t", priority=value)

        assert error_locs(exc_info) == {"priority"}

    def test_title_not_coerced_from_int(self) -> None:
        """Test that an int is not coerced to a str title."""
        with pytest.raises(ValidationError) as exc_info:
            ToDoBase(title=123, priority=1)  # pyrefly: ignore[bad-argument-type]

        assert error_locs(exc_info) == {"title"}

    def test_empty_title_allowed(self) -> None:
        """Document that title has no min length."""
        assert ToDoBase(title="", priority=1).title == ""

    @pytest.mark.parametrize(("value", "expected"), [("true", True), ("0", False), (1, True)])
    def test_completed_coercion(self, value: Any, expected: bool) -> None:
        """Test lax coercion of completed to bool."""
        assert ToDoBase(title="t", priority=1, completed=value).completed is expected


class TestToDoCreate:
    """Tests for ToDoCreate validation and serialization."""

    def test_valid(self) -> None:
        """Test valid construction."""
        uid = uuid4()
        todo = ToDoCreate(title="t", priority=2, user_id=uid)

        assert todo.user_id == uid
        assert todo.completed is False

    def test_user_id_required(self) -> None:
        """Test that user_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            ToDoCreate(title="t", priority=1)  # pyrefly: ignore[missing-argument]

        assert error_locs(exc_info) == {"user_id"}

    def test_user_id_from_string(self) -> None:
        """Test that a UUID string is coerced to UUID."""
        uid = uuid4()
        todo = ToDoCreate(title="t", priority=1, user_id=str(uid))  # pyrefly: ignore[bad-argument-type]

        assert isinstance(todo.user_id, UUID)
        assert todo.user_id == uid

    def test_invalid_user_id(self) -> None:
        """Test that a malformed UUID is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ToDoCreate(title="t", priority=1, user_id="nope")  # pyrefly: ignore[bad-argument-type]

        assert error_locs(exc_info) == {"user_id"}

    @pytest.mark.parametrize("mode", ["python", "json"])
    def test_user_id_serialized_as_str(self, mode: str) -> None:
        """Test that the field serializer emits user_id as str in both modes."""
        uid = uuid4()
        data = ToDoCreate(title="t", priority=1, user_id=uid).model_dump(mode=mode)  # pyrefly: ignore[bad-argument-type]

        assert data["user_id"] == str(uid)
        assert type(data["user_id"]) is str

    def test_json_output(self) -> None:
        """Test that model_dump_json contains the stringified user_id."""
        uid = uuid4()
        payload = ToDoCreate(title="t", priority=1, user_id=uid).model_dump_json()

        assert f'"user_id":"{uid}"' in payload

    def test_attribute_remains_uuid(self) -> None:
        """Test that serialization does not alter the stored attribute."""
        uid = uuid4()
        todo = ToDoCreate(title="t", priority=1, user_id=uid)
        todo.model_dump()

        assert isinstance(todo.user_id, UUID)


class TestToDoUpdate:
    """Tests for ToDoUpdate validation."""

    def test_empty_update(self) -> None:
        """Test that all fields are optional and default to None."""
        update = ToDoUpdate()

        assert update.model_dump() == {"title": None, "description": None, "priority": None, "completed": None}
        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_dump_exclude_unset(self) -> None:
        """Test that only provided fields are dumped with exclude_unset."""
        update = ToDoUpdate(completed=True, priority=9)

        assert update.model_dump(exclude_unset=True) == {"completed": True, "priority": 9}

    def test_explicit_none_is_set(self) -> None:
        """Test that an explicit None counts as set."""
        assert ToDoUpdate(description=None).model_dump(exclude_unset=True) == {"description": None}

    def test_type_failure(self) -> None:
        """Test that an invalid priority still fails."""
        with pytest.raises(ValidationError) as exc_info:
            ToDoUpdate(priority="high")  # pyrefly: ignore[bad-argument-type]

        assert error_locs(exc_info) == {"priority"}

    def test_priority_coercion(self) -> None:
        """Test that a numeric string is coerced."""
        assert ToDoUpdate(priority="7").priority == 7  # pyrefly: ignore[bad-argument-type]

    def test_user_id_not_updatable(self) -> None:
        """Test that user_id is not part of the update model."""
        assert "user_id" not in ToDoUpdate.model_fields


class TestToDoTable:
    """Light checks on the ToDo table model, without a database."""

    def test_tablename(self) -> None:
        """Test the table name."""
        assert ToDo.__tablename__ == "todos"

    def test_defaults_and_id(self) -> None:
        """Test defaults and unique id generation."""
        uid = uuid4()
        first = ToDo(title="t", priority=1, user_id=uid)
        second = ToDo(title="t", priority=1, user_id=uid)

        assert isinstance(first.id, UUID)
        assert first.id != second.id
        assert first.completed is False
        assert first.description is None

    def test_user_id_serialized_as_str(self) -> None:
        """Test that the inherited serializer applies to the table model."""
        uid = uuid4()

        assert ToDo(title="t", priority=1, user_id=uid).model_dump()["user_id"] == str(uid)

    def test_foreign_key(self) -> None:
        """Test the user_id foreign key and primary key on the table."""
        columns = ToDo.__table__.columns  # pyrefly: ignore[missing-attribute]
        fks = {fk.target_fullname: fk.ondelete for fk in columns["user_id"].foreign_keys}

        assert fks == {"users.id": "CASCADE"}
        assert columns["id"].primary_key is True
        assert columns["user_id"].index is True
