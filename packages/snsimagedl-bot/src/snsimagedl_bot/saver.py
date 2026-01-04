from typing import Protocol, Any

__all__ = (
    "Saver",
)


class Saver[T: Any](Protocol):
    async def save(self, message: T, /) -> None:
        raise NotImplemented
