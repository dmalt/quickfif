"""CLI documentation."""
from typing import Final

from quickfif.config import Ftype

FTYPE_HELP: Final = "Manually specify file type instead of guessing it from extension"
UNSUPPORTED_FTYPE_ERROR_MSG: Final = (
    "Can`t determine file type by extension."
    + "Try specifying the type manually via --ftype option."
)


def get_ftype_choices() -> list[str]:
    """Get supported file types."""
    return [str(ft) for ft in Ftype]
