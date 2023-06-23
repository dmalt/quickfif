"""Utilities for inspecting objects in IPython console."""
from typing import Any

import IPython
from traitlets.config.loader import Config


def embed_ipython(namespace: dict[str, Any]) -> None:
    """Embed IPython console with populated namespace."""
    config = Config()
    config.InteractiveShell.banner2 = _gen_ipython_header(namespace)  # pyright: ignore
    IPython.start_ipython(argv=[], user_ns=namespace, config=config)


def _gen_ipython_header(namespace: dict[str, Any]) -> str:
    header = "Populated variables"
    underline = "-" * len(header)
    banner = [header, underline]
    for var_name, var_val in namespace.items():
        banner.append("{name:10}:    {val}".format(name=var_name, val=var_val))
    return "\n".join(banner)
