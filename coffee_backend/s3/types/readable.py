from typing import Protocol


class Readable(Protocol):
    """Protocol for readable objects."""

    def read(self, size: int) -> bytes:
        """Read bytes from object."""
