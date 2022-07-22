Tools to preview `.fif` files (raw data, epochs, annotations, ica solutions)
info from terminal, inspect them in ipython console and more.
Ready for integration with CLI-based file managers, such as
[ranger](https://github.com/ranger/ranger).


Quickstart
==========

To install the tools, run

```bash
python3 -m pip install --user pipx
pipx install git+https://github.com/dmalt/mne-cli-tools.git
```

The `mct` command should now be available in the terminal.

To preview a file, run

```bash
mct <filename.fif>
```

![preview example](https://github.com/dmalt/mne-cli-tools/blob/master/docs/preview.png?raw=true)

To inspect the file in ipython console, run

```bash
mct <filename.fif> inspect
```

![inspect example](https://github.com/dmalt/mne-cli-tools/blob/master/docs/inspect.png?raw=true)

From the ipython header you can see, that `fname` and `raw` objects were populated.

Ranger integration
------------------

To enable `.fif` files preview, in `ranger/scope.sh` modify the extension-handling section:
```bash
case "$extension" in
    # ...
    fif)
        try mct $path && { dump | trim; exit 0; } || exit 1;;
    # ...
esac
```

For opening files from `ranger`, go to `ranger/rifle.conf` and add
```
ext fif = mct -- "$1" inspect
```

For a complete ranger configuration example, checkout my [ranger configuration](https://github.com/dmalt/dotfiles/tree/master/ranger)


Other functionality
===================

### Splits-awere copying for large `.fif` files.

`.fif` format doesn't support files larger than 2 GB. To bypass this issue,
large `.fif` files are stored in the so-called splits, when the file is divided
into parts under 2 GB which are stored separately. The drawback of such scheme
is that the first file has to internally maintain links to the next splits
which are tied to the filenames. It makes splits renaming problematic, since
the reanming breaks the internal filename links. To copy the large `.fif` file
properly, we need to read it and then write with a new file name. The following
command is a shortcut for that:

```
mct <filename_meg.fif> copy <dst_meg.fif>
```


### Supported file types and configuration

Under the hood `mct` relies on file extensions to determine the correct type.
These extensions and the associated types are set up via plugins, which are specified
in the configuration `.json` file.

To show current configuration, run

```bash
mct --show-config
```

The command will show current configuration in json format, e.g:
```json
{
  "ftype_plugins": {
    "mne_cli_tools.mne_types.raw_fif": {
      "extensions": [
        "raw.fif",
        "raw_sss.fif",
        "raw_tsss.fif",
        "_meg.fif",
        "_eeg.fif",
        "_ieeg.fif",
        "raw.fif.gz",
        "raw_sss.fif.gz",
        "raw_tsss.fif.gz",
        "_meg.fif.gz",
        "_eeg.fif.gz",
        "_ieeg.fif.gz"
      ]
    },
    "mne_cli_tools.mne_types.annotations": {
      "extensions": [
        "_annot.fif",
        "-annot.fif"
      ]
    },
    "mne_cli_tools.mne_types.epochs": {
      "extensions": [
        "-epo.fif",
        "_epo.fif"
      ]
    },
    "mne_cli_tools.mne_types.ica": {
      "extensions": [
        "_ica.fif",
        "-ica.fif"
      ]
    }
  }
}
```
To specify a custom configuration, use `--config` flag.


### Extending mct

`mct` utilized plugin-based architecture. It can be extended via creating an external module
handling a particular file type and configuring the associated extensions via the configuration
`.json` file (see the section above).

Below is a plugin example for epochs type:

```python
from dataclasses import asdict, dataclass, field

import mne  # type: ignore

from mne_cli_tools import factory


@dataclass
class EpochsFif:
    fname: str
    epochs: mne.Epochs = field(init=False)

    def __post_init__(self):
        self.epochs = mne.read_epochs(self.fname, verbose="ERROR")  # pyright: ignore

    def __str__(self):
        return str(self.epochs.info)

    def to_dict(self):
        return asdict(self)


def initialize(extensions: list[str]) -> None:
    for ext in extensions:
        factory.register(ext, EpochsFif)
```

To add this plugin to `pipx` virtualenv, use `pipx inject`. Then, create a
custom configuration from `mct --show-config` and specify your `ftype_plugin` and the associated
extensions.
