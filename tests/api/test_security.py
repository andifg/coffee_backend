from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aioresponses import aioresponses
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials

from coffee_backend.api.security import VerifyToken
from coffee_backend.exceptions.exceptions import UnauthenticatedException

fake_request = Request(
    {
        "type": "http",
        "method": "GET",
        "headers": {"host": "example.com"},
        "path": "/test",
        "query_string": b"param1=value1&param2=value2",
    }
)

token = HTTPAuthorizationCredentials(
    scheme="Bearer",
    credentials="eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ6dW9yak"
    + "xGX3pvTEdCeXctN1ZrRkVXbEVTRHJkYmlLb1FqVlZCTkI2TnNVIn0.eyJleHAiOjE3MD"
    + "E2NzY4OTcsImlhdCI6MTcwMTY3NjU5NywiYXV0aF90aW1lIjoxNzAxNjc2NTk2LCJqdG"
    + "kiOiJiYTI2ODQ4Mi01ZDUxLTQzZjEtOTNhOS00N2ZhNTg3ZDAwZTEiLCJpc3MiOiJodH"
    + "RwOi8vbG9jYWxob3N0OjgwODAvcmVhbG1zL0NvZmZlZS1BcHAiLCJhdWQiOlsicmVhY3"
    + "QtYXBwIiwiYWNjb3VudCJdLCJzdWIiOiI4NGFiZmJmYS1mYzliLTQxOWItYWJiNS1iZj"
    + "k3OTVmYjAwYzgiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJyZWFjdC1hcHAiLCJzZXNzaW"
    + "9uX3N0YXRlIjoiYjViZjg1OWMtYmFmOC00ZTU0LWJmYzUtYzQyZWM2NDkwOWUxIiwiYW"
    + "NyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwOi8vbG9jYWxob3N0OjUxNzMiXS"
    + "wicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwiZGVmYXVsdC"
    + "1yb2xlcy1kZW1vIiwiYnViYXJvbGUiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3"
    + "VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLC"
    + "JtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3"
    + "BlbmlkIHByb2ZpbGUgcmVhY3QtYXBwLWF1ZGllbmNlIGVtYWlsIGFkZHJlc3MiLCJzaW"
    + "QiOiJiNWJmODU5Yy1iYWY4LTRlNTQtYmZjNS1jNDJlYzY0OTA5ZTEiLCJhZGRyZXNzIj"
    + "p7fSwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJ0ZXN0IHRlc3QiLCJwcmVmZX"
    + "JyZWRfdXNlcm5hbWUiOiJ0ZXN0IiwiZ2l2ZW5fbmFtZSI6InRlc3QiLCJmYW1pbHlfbm"
    + "FtZSI6InRlc3QiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.BAOIA5N8vPfYT5Y"
    + "XYV3ujepRUjXQq33WYlAkaLJsOz4swF9QFbWcb1TemOcHdTbkYoJbfiS2x64Jv9sRLMvP"
    + "w_TQeqCddAo5RgktPsIqqzYoZfuRtQ9_yobPXXl6bptpfYUghA2BPAODEU3jZBhAmt06"
    + "wRsvvwdMxHg0VlpuTGOVSupoK2AHATf-PQ9zx8untCZEaXJHneO-rMPbTbYJJfNz2Z31"
    + "wj8G-011k2xs7Obnwh008mBwn7YQJrPZIP9Xruezlkqa-RQugS4n1oKQztwAVSXMebWp"
    + "0Sv3R-6_ey1YR1BJynm6B0rkbaJ9zu4T_dAbD3rKQ7R4Kz-EKc6YZA",
)


@patch("jwt.decode")
@pytest.mark.asyncio
async def test_verify_token_verify_successfull_case(
    jwt_decode_mock: MagicMock,
    caplog: pytest.LogCaptureFixture,
    verify_token_test_class: VerifyToken,
) -> None:
    """Test the VerifyToken.verify method for a successful case.

    This test case uses the @patch decorator to mock the jwt.decode function.
    It verifies that the VerifyToken.verify method correctly handles a
    successful token verification.

    Args:
        jwt_decode_mock (MagicMock): Mock for the jwt.decode function.
        caplog (pytest.LogCaptureFixture): Fixture for capturing log messages.
    """
    jwks_client_mock = MagicMock()
    singing_key_mock = MagicMock()

    jwt_decode_mock.return_value = {
        "scope": "openid profile email address roles",
        "preferred_username": "test",
    }

    jwks_client_mock.get_signing_key_from_jwt.return_value = singing_key_mock

    verify_token_test_class.jwks_client = jwks_client_mock

    with aioresponses() as mocked_responses:
        mocked_responses.get(
            verify_token_test_class.userinfo_endpoint, status=200
        )

        await verify_token_test_class.verify(request=fake_request, token=token)

    jwt_decode_mock.assert_called_once_with(
        token.credentials,
        singing_key_mock.key,
        algorithms=["RS256"],
        issuer=verify_token_test_class.issuer_url,
        audience=verify_token_test_class.client_id,
    )

    # pylint: disable=C0301
    assert (
        "Authenticated user {'test'} with scopes {'openid profile email address roles'}"
        in caplog.messages
    )
    # pylint: enable=C0301


@patch("jwt.decode")
@pytest.mark.asyncio
async def test_verify_token_verify_unsucessfull_decode(
    jwt_decode_mock: MagicMock, verify_token_test_class: VerifyToken
) -> None:
    """
    Test case for verifying unsuccessful token decoding.

    Args:
        jwt_decode_mock (MagicMock): Mock object for jwt.decode.
    """

    jwks_client_mock = MagicMock()
    singing_key_mock = MagicMock()
    _check_token_validity_mock = AsyncMock()

    jwks_client_mock.get_signing_key_from_jwt.return_value = singing_key_mock
    verify_token_test_class.jwks_client = jwks_client_mock
    # pylint: disable=W0212
    # pylint: disable=C0301
    verify_token_test_class._check_token_validity = _check_token_validity_mock  # type: ignore
    # pylint: enable=C0301
    # pylint: enable=W0212
    jwt_decode_mock.side_effect = Exception("Invalid token")

    with pytest.raises(UnauthenticatedException):
        await verify_token_test_class.verify(request=fake_request, token=token)

    jwt_decode_mock.assert_called_once_with(
        token.credentials,
        singing_key_mock.key,
        algorithms=["RS256"],
        issuer=verify_token_test_class.issuer_url,
        audience=verify_token_test_class.client_id,
    )


@patch("jwt.decode")
@pytest.mark.asyncio
async def test_verify_token_verify_deleted_session_on_idp(
    jwt_decode_mock: MagicMock, verify_token_test_class: VerifyToken
) -> None:
    """Test the VerifyToken.verify method for a deleted session on the IDP.

    Test case simulates the scenario that idp responds with a unsuccessful
    status code.

    Args:
        jwt_decode_mock (MagicMock): Mock for the jwt.decode function.

    """

    jwks_client_mock = MagicMock()
    singing_key_mock = MagicMock()

    jwks_client_mock.get_signing_key_from_jwt.return_value = singing_key_mock
    verify_token_test_class.jwks_client = jwks_client_mock

    with aioresponses() as mocked_responses:
        mocked_responses.get(
            verify_token_test_class.userinfo_endpoint, status=401
        )

        with pytest.raises(UnauthenticatedException):
            await verify_token_test_class.verify(
                request=fake_request, token=token
            )

    jwt_decode_mock.assert_called_once_with(
        token.credentials,
        singing_key_mock.key,
        algorithms=["RS256"],
        issuer=verify_token_test_class.issuer_url,
        audience=verify_token_test_class.client_id,
    )


@pytest.mark.asyncio
async def test_verify_token_verify_no_token(
    verify_token_test_class: VerifyToken,
) -> None:
    """Test the VerifyToken.verify method without providing a token.

    This test case uses the @patch decorator to mock the jwt.decode function.
    It verifies that the VerifyToken.verify method correctly raises an
    UnauthenticatedException when no token is provided.

    Args:
        jwt_decode_mock (MagicMock): Mock for the jwt.decode function.
    """

    with pytest.raises(UnauthenticatedException):
        # pylint: disable=C0301
        await verify_token_test_class.verify(request=fake_request, token=None)  # type: ignore
        # pylint: enable=C0301
