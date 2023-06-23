"""Plugin handling mne.Annotations."""
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

import mne  # type: ignore
import pandas as pd

from mne_cli_tools import factory

pd.set_option("display.float_format", lambda xx: "{0:.2f}".format(xx))


@dataclass
class AnnotsFif(object):
    """MneType implementation for mne.Annotations."""

    fname: str
    annots: mne.Annotations = field(init=False)

    def __post_init__(self) -> None:
        """Read the annotations."""
        self.annots = mne.read_annotations(self.fname)  # noqa: WPS601

    def __str__(self) -> str:
        """Annotations string representation."""
        return str(get_annots_pandas_summary(self.annots))

    def to_dict(self) -> dict[str, Any]:
        """Convert object to dictionary."""
        return asdict(self)


def get_annots_pandas_summary(annots: mne.Annotations) -> pd.DataFrame:
    """Get annotations summary in pandas DataFrame format."""
    df = annots.to_data_frame()
    df_groups = df.groupby("description").duration.describe()
    total_series = df.duration.describe()
    total_series.name = "Total"
    total_df = pd.DataFrame(total_series).T
    joint_df = pd.concat([df_groups, total_df])
    joint_df["count"] = joint_df["count"].astype(int)
    return joint_df


def initialize(extensions: Iterable[str]) -> None:
    """Register extenstions for the plugin."""
    for ext in extensions:
        factory.register(ext, AnnotsFif)
