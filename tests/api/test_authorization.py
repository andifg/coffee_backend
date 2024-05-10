import pytest
from fastapi import HTTPException, Request
from uuid_extensions.uuid7 import uuid7

from coffee_backend.api.authorization import authorize_coffee_edit_delete


def test_authorize_coffee_edit_delete_with_matching_user() -> None:
    """Test authorize_coffee_edit_delete.

    Test that no exception is raised when coffee_id is the same as the user_id.
    """

    uuid = uuid7()

    fake_request = Request(
        {
            "type": "http",
            "method": "GET",
            "headers": {"host": "example.com"},
            "path": "/test",
            "query_string": b"param1=value1&param2=value2",
            "state": {
                "token": {"realm_access": {"roles": ["user"]}, "sub": str(uuid)}
            },
        }
    )

    authorize_coffee_edit_delete(fake_request, uuid)


def test_authorize_coffee_edit_delete_with_admin_user() -> None:
    """Test authorize_coffee_edit_delete.

    Test that no exception is raised when the user is an admin.
    """

    uuid = uuid7()

    fake_request = Request(
        {
            "type": "http",
            "method": "GET",
            "headers": {"host": "example.com"},
            "path": "/test",
            "query_string": b"param1=value1&param2=value2",
            "state": {
                "token": {"realm_access": {"roles": ["admin"]}, "sub": "test"}
            },
        }
    )

    authorize_coffee_edit_delete(fake_request, uuid)


def test_authorize_coffee_edit_delete_with_unauthorized_user() -> None:
    """Test authorize_coffee_edit_delete."""

    uuid = uuid7()

    fake_request = Request(
        {
            "type": "http",
            "method": "GET",
            "headers": {"host": "example.com"},
            "path": "/test",
            "query_string": b"param1=value1&param2=value2",
            "state": {"token": {"realm_access": {"roles": []}, "sub": "test"}},
        }
    )

    with pytest.raises(HTTPException) as error:
        authorize_coffee_edit_delete(fake_request, uuid)

    assert error.value.status_code == 403
    assert (
        error.value.detail
        == "You are not authorized to edit or delete this coffee."
    )
