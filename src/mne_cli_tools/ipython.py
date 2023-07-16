"""Utilities for inspecting objects in IPython console."""
from typing import Any

import IPython
import matplotlib
from returns.io import impure
from traitlets.config.loader import Config


@impure
def embed_ipython(ns: dict[str, Any]) -> None:  # type: ignore[misc]
    """
    Embed IPython console with populated namespace.

    Before launching IPython, setup header showing the populated variables.

    """
    matplotlib.use("TkAgg")
    cfg = Config()  # type: ignore[no-untyped-call]
    cfg.InteractiveShell.banner2 = _gen_ipython_header(ns)  # pyright: ignore
    IPython.start_ipython(argv=[], user_ns=ns, config=cfg)  # type: ignore[no-untyped-call]


def _gen_ipython_header(namespace: dict[str, Any]) -> str:  # type: ignore[misc]
    header = "Populated variables"
    underline = "-" * len(header)
    banner = [header, underline]
    for var_name, var_val in namespace.items():
        banner.append("{name:10}:    {val}".format(name=var_name, val=var_val))
    return "\n".join(banner)
