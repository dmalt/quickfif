"""Plugin handling mne.Annotations."""
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from mne import Annotations, read_annotations
from returns.io import impure_safe


@dataclass
class AnnotsFif(object):
    """MneType implementation for mne.Annotations."""

    fpath: Path
    annots: Annotations

    def __str__(self) -> str:
        """Annotations string representation."""
        return get_annots_summary(self.annots)

    def to_dict(self) -> dict[str, Path | Annotations]:
        """Convert to namespace dictionary."""
        return asdict(self)


def get_annots_summary(annots: Annotations) -> str:
    """Get annotations summary."""
    df = annots.to_data_frame()
    df_groups = df.groupby("description").duration.describe()
    total_series = df.duration.describe()
    total_series.name = "Total"
    total_df = pd.DataFrame(total_series).T
    joint_df = pd.concat([df_groups, total_df])
    joint_df["count"] = joint_df["count"].astype(int)
    return joint_df.to_string(float_format=lambda x: "{0:.2f}".format(x))


@impure_safe
def read(fpath: Path) -> AnnotsFif:
    """Read the annotations."""
    annots = read_annotations(str(fpath))  # noqa: WPS601 (shadowed class attr)
    return AnnotsFif(fpath, annots)
