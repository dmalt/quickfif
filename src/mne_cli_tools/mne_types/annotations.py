"""Plugin handling mne.Annotations."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

import pandas as pd
from mne import Annotations, read_annotations

from mne_cli_tools.types import Ext, Ftype

pd.set_option("display.float_format", lambda xx: "{0:.2f}".format(xx))

EXTENSIONS: Final = (Ext("_annot.fif"), Ext("-annot.fif"))
FTYPE_ALIAS: Final = Ftype("annots")


@dataclass
class AnnotsFif(object):
    """MneType implementation for mne.Annotations."""

    fpath: Path
    annots: Annotations

    def __str__(self) -> str:
        """Annotations string representation."""
        return str(get_annots_pandas_summary(self.annots))

    def to_dict(self) -> dict[str, Path | Annotations]:
        """Convert to namespace dictionary."""
        return asdict(self)


def get_annots_pandas_summary(annots: Annotations) -> pd.DataFrame:
    """Get annotations summary in pandas DataFrame format."""
    df = annots.to_data_frame()
    df_groups = df.groupby("description").duration.describe()
    total_series = df.duration.describe()
    total_series.name = "Total"
    total_df = pd.DataFrame(total_series).T
    joint_df = pd.concat([df_groups, total_df])
    joint_df["count"] = joint_df["count"].astype(int)
    return joint_df


def read(fpath: Path) -> AnnotsFif:
    """Read the annotations."""
    annots = read_annotations(str(fpath))  # noqa: WPS601 (shadowed class attr)
    return AnnotsFif(fpath, annots)
