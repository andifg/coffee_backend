from typing import Any, Coroutine, Protocol


class Readable(Protocol):
    """Protocol for readable objects."""

    def read(self, size: int) -> bytes | Coroutine[Any, Any, bytes]:
        """Read bytes from object."""
