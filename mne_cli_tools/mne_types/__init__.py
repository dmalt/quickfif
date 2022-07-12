from typing import Any, Protocol


class MneType(Protocol):
    def __str__(self) -> str:
        ...

    def to_dict(self) -> dict[str, Any]:
        ...
