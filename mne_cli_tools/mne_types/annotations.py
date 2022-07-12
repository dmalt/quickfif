from dataclasses import asdict, dataclass, field

import mne  # type: ignore
import pandas as pd

from mne_cli_tools import factory

pd.set_option('display.float_format', lambda x: '%.2f' % x)


@dataclass
class AnnotsFif:
    fname: str
    annots: mne.Annotations = field(init=False)

    def __post_init__(self):
        self.annots = mne.read_annotations(self.fname)

    def __str__(self):
        return str(get_annots_pandas_summary_str(self.annots))

    def to_dict(self):
        return asdict(self)


def get_annots_pandas_summary_str(annots):
    df = annots.to_data_frame()
    df_groups = df.groupby("description").duration.describe()
    total_series = df.duration.describe()
    total_series.name = "Total"
    total_df = pd.DataFrame(total_series).T
    joint_df = pd.concat([df_groups, total_df])
    joint_df['count'] = joint_df['count'].astype(int)
    return joint_df


def initialize(extensions: list[str]) -> None:
    for ext in extensions:
        factory.register(ext, AnnotsFif)
