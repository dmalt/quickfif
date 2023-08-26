# Quickfif

[![Tests](https://github.com/dmalt/quickfif/workflows/Tests/badge.svg)](https://github.com/dmalt/quickfif/actions?workflow=Tests)

Quick operations on `.fif` files from the terminal:

- preview
- inspect in ipython console
- splits-aware exports and 'saveas'

Ready for integration with CLI-based file managers, such as
[ranger](https://github.com/ranger/ranger).

## Quickstart

To install `quickfif`, run

```bash
python3 -m pip install --user pipx
python3 -m pipx install git+https://github.com/dmalt/quickfif.git
```

The `qf` command should now be available in the terminal.

To preview a file:

```bash
qfif <filename.fif>
```

To inspect the file in ipython console:

```bash
qfif <filename.fif> inspect
```

### Splits-aware copying for large `.fif` files

`.fif` format doesn't support files larger than 2 GB. To bypass this issue,
large `.fif` files are stored in **splits**: separate files under 2 GB. To keep
track of its parts the first (main) file has to internally maintain filenames
of its parts. It makes splits renaming problematic, since the reanming breaks
the internal filename links. To rename a large `.fif` file properly, we need to
read it and then write with a new file name. The following command is a
shortcut for that:

```bash
qfif <filename_meg.fif> saveas <dst_meg.fif>
```

### Ranger integration

To enable `.fif` files preview, in `ranger/scope.sh` edit the
extension-handling section:

```bash
case "$extension" in
    # ...
    fif)
        try qfif "$path" && { dump | trim; exit 0; } || exit 1;;
    # ...
esac
```

For opening files from `ranger`, go to `ranger/rifle.conf` and add

```conf
ext fif = qfif -- "$1" inspect
```

For a complete ranger configuration example,
checkout my [ranger configuration](https://github.com/dmalt/dotfiles/tree/master/ranger)
