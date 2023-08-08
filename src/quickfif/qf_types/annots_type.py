"""Plugin handling mne.Annotations."""
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

import pandas as pd
from mne import Annotations, read_annotations

EXTENSIONS: Final[tuple[str, ...]] = ("_annot.fif", "-annot.fif")


SUMMARY_HEADER: Final = "Annotations duration statistics"


@dataclass
class QfAnnots(object):
    """QfType implementation for mne.Annotations."""

    fpath: Path
    annots: Annotations

    @property
    def summary(self) -> str:
        """Annotations string representation."""
        underline = "-" * len(SUMMARY_HEADER)
        return "\n".join([SUMMARY_HEADER, underline, get_annots_summary(self.annots)])

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


def read(fpath: Path) -> QfAnnots:
    """Read the annotations."""
    annots = read_annotations(str(fpath))  # noqa: WPS601 (shadowed class attr)
    return QfAnnots(fpath, annots)


def save(qf_obj: QfAnnots, dst: Path, overwrite: bool) -> None:
    """Save ICA solution."""
    if dst.is_dir():
        dst = dst / qf_obj.fpath.name
    qf_obj.annots.save(fname=dst, overwrite=overwrite)
