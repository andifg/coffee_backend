class ObjectNotFoundError(Exception):
    """Custom exception for CRUD Database empty results."""

    def __init__(self, message: str):
        super().__init__(message)
