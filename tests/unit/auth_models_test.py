from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.auth.models import User, UserBase, UserCreate, UserCreatePrivate, UserRead, UserUpdate
from src.auth.users.enum import UserRole

VALID_USER: dict[str, Any] = {
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "username": "ada",
}


def make_user(**overrides: Any) -> dict[str, Any]:
    """Build a valid user payload with optional overrides."""
    return {**VALID_USER, **overrides}


def error_locs(exc_info: pytest.ExceptionInfo[ValidationError]) -> set[str]:
    """Return the set of field names that failed validation."""
    return {str(err["loc"][0]) for err in exc_info.value.errors()}


class TestUserRole:
    """Tests for the UserRole enum."""

    def test_values(self) -> None:
        """Test the enum members and their values."""
        assert {role.name: role.value for role in UserRole} == {"ADMIN": "admin", "USER": "user"}

    def test_is_str(self) -> None:
        """Test that members compare equal to plain strings."""
        assert UserRole.ADMIN == "admin"
        assert UserRole("user") is UserRole.USER

    def test_invalid_value(self) -> None:
        """Test that an unknown value raises ValueError."""
        with pytest.raises(ValueError):
            UserRole("superuser")


class TestUserBase:
    """Tests for UserBase validation."""

    def test_valid_with_defaults(self) -> None:
        """Test valid construction and default values."""
        user = UserBase(**make_user())

        assert user.first_name == "Ada"
        assert user.is_active is True
        assert user.role == UserRole.USER

    def test_default_role_is_not_converted(self) -> None:
        """Document that use_enum_values does not apply to unvalidated defaults: the default stays an enum member."""
        user = UserBase(**make_user())

        assert user.role is UserRole.USER
        assert user.role == "user"

    @pytest.mark.parametrize("role", ["admin", UserRole.ADMIN])
    def test_use_enum_values_input(self, role: str | UserRole) -> None:
        """Test that enum or string input is stored as a plain string."""
        user = UserBase(**make_user(role=role))

        assert type(user.role) is str
        assert user.role == "admin"
        assert user.model_dump()["role"] == "admin"

    @pytest.mark.parametrize("role", ["superuser", "ADMIN", "", None, 1])
    def test_invalid_role(self, role: Any) -> None:
        """Test that an invalid role is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**make_user(role=role))

        assert error_locs(exc_info) == {"role"}

    @pytest.mark.parametrize("field", ["first_name", "last_name"])
    @pytest.mark.parametrize(("length", "valid"), [(0, False), (1, True), (50, True), (51, False)])
    def test_name_length_boundaries(self, field: str, length: int, valid: bool) -> None:
        """Test min (1) and max (50) name lengths."""
        payload = make_user(**{field: "a" * length})

        if valid:
            assert getattr(UserBase(**payload), field) == "a" * length
        else:
            with pytest.raises(ValidationError) as exc_info:
                UserBase(**payload)
            assert error_locs(exc_info) == {field}

    @pytest.mark.parametrize(("length", "valid"), [(2, False), (3, True), (50, True), (51, False)])
    def test_username_length_boundaries(self, length: int, valid: bool) -> None:
        """Test min (3) and max (50) username lengths."""
        payload = make_user(username="u" * length)

        if valid:
            assert UserBase(**payload).username == "u" * length
        else:
            with pytest.raises(ValidationError) as exc_info:
                UserBase(**payload)
            assert error_locs(exc_info) == {"username"}

    @pytest.mark.parametrize(("total_length", "valid"), [(120, True), (121, False)])
    def test_email_max_length(self, total_length: int, valid: bool) -> None:
        """Test the email max length of 120 characters."""
        domain = "@example.com"
        email = "a" * (total_length - len(domain)) + domain
        assert len(email) == total_length

        if valid:
            assert UserBase(**make_user(email=email)).email == email
        else:
            with pytest.raises(ValidationError) as exc_info:
                UserBase(**make_user(email=email))
            assert error_locs(exc_info) == {"email"}

    @pytest.mark.parametrize("email", ["not-an-email", "missing@tld", "@example.com", "a@", "", "a b@example.com"])
    def test_invalid_email(self, email: str) -> None:
        """Test that malformed emails are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**make_user(email=email))

        assert error_locs(exc_info) == {"email"}

    @pytest.mark.parametrize("field", ["first_name", "last_name", "email", "username"])
    def test_missing_required_field(self, field: str) -> None:
        """Test that each required field must be provided."""
        payload = make_user()
        del payload[field]

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**payload)

        assert error_locs(exc_info) == {field}

    @pytest.mark.parametrize(("value", "expected"), [("true", True), ("false", False), (1, True), (0, False)])
    def test_is_active_coercion(self, value: Any, expected: bool) -> None:
        """Test lax coercion of is_active to bool."""
        assert UserBase(**make_user(is_active=value)).is_active is expected

    def test_is_active_invalid(self) -> None:
        """Test that a non-boolean-like is_active fails."""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**make_user(is_active="maybe"))

        assert error_locs(exc_info) == {"is_active"}

    @pytest.mark.parametrize("field", ["first_name", "username"])
    def test_non_string_fails(self, field: str) -> None:
        """Test that non-string values are not coerced into strings."""
        with pytest.raises(ValidationError):
            UserBase(**make_user(**{field: 12345}))


class TestUserCreate:
    """Tests for UserCreate validation."""

    def test_valid(self) -> None:
        """Test valid construction including password."""
        user = UserCreate(**make_user(password="p" * 12))

        assert user.password == "p" * 12
        assert user.role == "user"

    @pytest.mark.parametrize(
        ("length", "valid"),
        [(11, False), (12, True), (72, True), (73, False)],
    )
    def test_password_length_boundaries(self, length: int, valid: bool) -> None:
        """Test password min (12) and max (72) lengths."""
        payload = make_user(password="x" * length)

        if valid:
            assert len(UserCreate(**payload).password) == length
        else:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(**payload)
            assert error_locs(exc_info) == {"password"}

    def test_password_required(self) -> None:
        """Test that password is required."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**make_user())

        assert error_locs(exc_info) == {"password"}

    def test_inherits_base_validation(self) -> None:
        """Test that base-class constraints still apply."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**make_user(username="ab", password="x" * 12))

        assert error_locs(exc_info) == {"username"}


class TestUserCreatePrivate:
    """Tests for UserCreatePrivate validation."""

    def test_valid(self) -> None:
        """Test valid construction with a password hash."""
        user = UserCreatePrivate(**make_user(password_hash="hashed"))

        assert user.password_hash == "hashed"

    def test_password_hash_required(self) -> None:
        """Test that password_hash is required."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreatePrivate(**make_user())

        assert error_locs(exc_info) == {"password_hash"}

    def test_no_length_limit_on_hash(self) -> None:
        """Test that password_hash has no length constraint."""
        assert len(UserCreatePrivate(**make_user(password_hash="h" * 500)).password_hash) == 500


class TestUserUpdate:
    """Tests for UserUpdate validation."""

    def test_empty_update_is_valid(self) -> None:
        """Test that all fields are optional and default to None."""
        update = UserUpdate()

        assert update.model_dump() == {
            "first_name": None,
            "last_name": None,
            "email": None,
            "username": None,
            "is_active": None,
            "role": None,
        }
        assert update.model_dump(exclude_unset=True) == {}

    def test_partial_dump_exclude_unset(self) -> None:
        """Test that only provided fields are dumped with exclude_unset."""
        update = UserUpdate(first_name="Grace", is_active=False)

        assert update.model_dump(exclude_unset=True) == {"first_name": "Grace", "is_active": False}

    def test_explicit_none_is_set(self) -> None:
        """Test that an explicit None counts as set."""
        update = UserUpdate(email=None)

        assert update.model_dump(exclude_unset=True) == {"email": None}

    def test_role_use_enum_values(self) -> None:
        """Test that role is stored as a plain string in updates."""
        update = UserUpdate(role=UserRole.ADMIN)

        assert type(update.role) is str
        assert update.model_dump(exclude_unset=True) == {"role": "admin"}

    def test_invalid_role(self) -> None:
        """Test that an invalid role is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(role="root")

        assert error_locs(exc_info) == {"role"}

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("first_name", ""),
            ("first_name", "a" * 51),
            ("last_name", ""),
            ("last_name", "a" * 51),
            ("username", "ab"),
            ("username", "a" * 51),
            ("email", "nope"),
        ],
    )
    def test_constraints_still_apply(self, field: str, value: str) -> None:
        """Test that constraints apply when a value is provided."""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**{field: value})

        assert error_locs(exc_info) == {field}

    @pytest.mark.parametrize(
        ("field", "value"),
        [("first_name", "a"), ("first_name", "a" * 50), ("username", "abc"), ("username", "a" * 50)],
    )
    def test_boundary_values_accepted(self, field: str, value: str) -> None:
        """Test that boundary values are accepted."""
        assert getattr(UserUpdate(**{field: value}), field) == value

    def test_password_not_accepted(self) -> None:
        """Test that an unknown password field is ignored, not stored."""
        update = UserUpdate(password="x" * 12)  # pyrefly: ignore[unexpected-keyword]

        assert "password" not in update.model_dump()


class TestUserRead:
    """Tests for UserRead validation."""

    def test_valid(self) -> None:
        """Test valid construction with an id."""
        uid = uuid4()
        user = UserRead(**make_user(id=uid))

        assert user.id == uid

    def test_id_from_string(self) -> None:
        """Test that a UUID string is coerced to UUID."""
        uid = uuid4()

        assert UserRead(**make_user(id=str(uid))).id == uid

    def test_id_required(self) -> None:
        """Test that id is required."""
        with pytest.raises(ValidationError) as exc_info:
            UserRead(**make_user())

        assert error_locs(exc_info) == {"id"}

    def test_invalid_id(self) -> None:
        """Test that a malformed UUID is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserRead(**make_user(id="not-a-uuid"))

        assert error_locs(exc_info) == {"id"}

    def test_json_serialization_of_uuid(self) -> None:
        """Test that the UUID is serialized as a string in JSON mode."""
        uid = uuid4()
        data = UserRead(**make_user(id=uid)).model_dump(mode="json")

        assert data["id"] == str(uid)
        assert data["role"] == "user"

    def test_python_dump_keeps_uuid(self) -> None:
        """Test that the UUID stays a UUID in python mode."""
        uid = uuid4()

        assert isinstance(UserRead(**make_user(id=uid)).model_dump()["id"], UUID)

    def test_no_password_fields(self) -> None:
        """Test that sensitive fields are not part of the read model."""
        fields = set(UserRead.model_fields)

        assert "password" not in fields
        assert "password_hash" not in fields

    def test_from_table_model(self) -> None:
        """Test validating a User table instance into UserRead."""
        user = User(**make_user(password_hash="h"))
        read = UserRead.model_validate(user, from_attributes=True)

        assert read.id == user.id
        assert read.username == "ada"


class TestUserTable:
    """Light checks on the User table model, without a database."""

    def test_tablename(self) -> None:
        """Test the table name."""
        assert User.__tablename__ == "users"

    def test_id_default_is_uuid(self) -> None:
        """Test that each instance gets a unique UUID id."""
        first = User(**make_user(password_hash="h"))
        second = User(**make_user(password_hash="h"))

        assert isinstance(first.id, UUID)
        assert first.id != second.id

    def test_defaults(self) -> None:
        """Test inherited defaults on the table model."""
        user = User(**make_user(password_hash="h"))

        assert user.is_active is True
        assert user.role == "user"

    def test_columns(self) -> None:
        """Test the column set and primary key."""
        columns = User.__table__.columns  # pyrefly: ignore[missing-attribute]

        expected = {"id", "first_name", "last_name", "email", "username", "is_active", "role", "password_hash"}
        assert expected <= set(columns.keys())
        assert columns["id"].primary_key is True
        assert columns["created_at"].nullable is False

    def test_table_model_does_not_validate_on_init(self) -> None:
        """Document that SQLModel table models skip validation at construction."""
        user = User(**make_user(username="x", password_hash="h"))

        assert user.username == "x"
