"""CLI documentation."""
from mne_cli_tools.config import Ftype

ftype_help = "Manually specify file type instead of guessing it from extension"


def get_ftype_choices() -> list[str]:
    """Get supported file types."""
    return [str(ft) for ft in Ftype]
