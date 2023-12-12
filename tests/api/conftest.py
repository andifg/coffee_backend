import pytest

from coffee_backend.api.security import VerifyToken


@pytest.fixture
def verify_token_test_class() -> VerifyToken:
    """Initialize the VerifyToken class for testing."""

    test_auth = VerifyToken(
        protocol="http",
        hostname="localhost",
        realm_name="Coffee-App",
        client_id="coffee-app",
        issuer_hostname="localhost",
        issuer_protocoll="http",
    )

    return test_auth
