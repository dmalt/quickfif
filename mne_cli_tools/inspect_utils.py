from typing import Any

import IPython
from traitlets.config.loader import Config


def gen_ipython_header(namespace: dict[str, Any]) -> str:
    header = "Populated variables"
    underline = "-" * len(header)
    banner = [header, underline]
    for k, v in namespace.items():
        banner.append(f"{k:10}:    {v}")
    return "\n".join(banner)


def embed(namespace: dict[str, Any]):
    c = Config()
    c.InteractiveShell.banner2 = gen_ipython_header(namespace)  # pyright: ignore
    IPython.start_ipython(argv=[], user_ns=namespace, config=c)
