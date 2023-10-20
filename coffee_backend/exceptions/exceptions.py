from fastapi import HTTPException, status


class ObjectNotFoundError(Exception):
    """Custom exception for CRUD Database empty results."""

    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedException(HTTPException):
    """Custom exception for Unauthorized access requests."""

    def __init__(self, detail: str) -> None:
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    """Custom exception for unauthenticated access requests."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Requires authentication",
        )
