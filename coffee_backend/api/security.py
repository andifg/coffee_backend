import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp
import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from coffee_backend.exceptions.exceptions import UnauthenticatedException


class VerifyToken:
    """Does all the token verification using PyJWT.

    This class provides functionality for verifying tokens using PyJWT and
    performing additional checks for token validity and claims.
    """

    def __init__(
        self,
        protocol: str,
        hostname: str,
        realm_name: str,
        client_id: str,
        issuer_hostname: str,
        issuer_protocoll: str,
    ) -> None:
        """Initializes a VerifyToken instance.

        Args:
            protocol (str): The protocol used for the base URL (e.g., "https").
            hostname (str): The hostname of the token issuer.
            realm_name (str): The name of the token realm.
            client_id (str): The client identifier.

        """
        base_url = f"{protocol}://{hostname}/realms/{realm_name}"
        jwks_url = f"{base_url}/protocol/openid-connect/certs"
        self.userinfo_endpoint = f"{base_url}/protocol/openid-connect/userinfo"
        self.issuer_url: str = (
            f"{issuer_protocoll}://{issuer_hostname}/realms/{realm_name}"
        )
        self.jwks_client = jwt.PyJWKClient(jwks_url)
        self.client_id = client_id

    async def verify(
        self,
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ) -> None:
        """Verifies the provided token.

        Args:
            request (Request): The FastAPI request object.
            security_scopes (SecurityScopes): The required security scopes.
            token (HTTPAuthorizationCredentials): The bearer token.

        """
        if token is None:
            logging.debug("No token provided in request")
            raise UnauthenticatedException

        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key

            logging.debug(
                "Time now: %s", datetime.now(tz=timezone.utc).timestamp()
            )

            payload: dict[str, Any] = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=["RS256"],
                issuer=self.issuer_url,
                audience=self.client_id,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": False,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )

            logging.debug("Decoded token payload: %s", payload)

            # Use userinfo endpoint for token validation
            await self._check_token_validity(token)

        except Exception as error:
            logging.debug("Token verification failed with error %s", error)
            raise UnauthenticatedException() from error

        logging.debug(
            "Authenticated user %s with scopes %s with token iat %s",
            payload["preferred_username"],
            payload["scope"],
            payload["iat"],
        )

        request.state.token = payload

    async def _check_token_validity(
        self, token: HTTPAuthorizationCredentials
    ) -> None:
        """Check whether the provided token is still active by sending a
            request to the introspection endpoint.

        Args:
            token (HTTPAuthorizationCredentials): The token to check.

        Raises:
            UnauthenticatedException: If the response status is not 200.

        """
        async with aiohttp.ClientSession() as session:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {token.credentials}",
            }

            logging.debug(
                "Sending request to %s with headers", self.userinfo_endpoint
            )

            async with session.get(
                self.userinfo_endpoint, headers=headers
            ) as response:
                if response.status != 200:
                    logging.debug(
                        "Token validation failed with status %s from %s",
                        response.status,
                        self.userinfo_endpoint,
                    )
                    raise UnauthenticatedException()
