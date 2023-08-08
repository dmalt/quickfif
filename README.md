# Quickfif

Quick operations on `.fif` files for the terminal:

- preview
- inspect in ipython console
- splits-aware exports and 'saveas'

Ready for integration with CLI-based file managers, such as
[ranger](https://github.com/ranger/ranger).

## Quickstart

To install the tools, run

```bash
python3 -m pip install --user pipx
pipx install git+https://github.com/dmalt/quickfif.git
```

The `qf` command should now be available in the terminal.

To preview a file, run

```bash
qfif <filename.fif>
```


To inspect the file in ipython console, run

```bash
qfif <filename.fif> inspect
```


From the ipython header you can see, that the loading script populated `fname`
and `raw` objects.

### Ranger integration

To enable `.fif` files preview, in `ranger/scope.sh` edit the
extension-handling section:

```bash
case "$extension" in
    # ...
    fif)
        try qfif $path && { dump | trim; exit 0; } || exit 1;;
    # ...
esac
```

For opening files from `ranger`, go to `ranger/rifle.conf` and add

```conf
ext fif = qfif -- "$1" inspect
```

For a complete ranger configuration example, checkout my [ranger configuration](https://github.com/dmalt/dotfiles/tree/master/ranger)

## Other functionality

### Splits-awere saving for large `.fif` files

`.fif` format doesn't support files larger than 2 GB. To bypass this issue,
large `.fif` files are stored in the so-called splits: parts under 2 GB stored
separately. To keep track of its parts the first (main) file has to internally
maintain filenames of the rest of the splits. It makes splits renaming
problematic, since the reanming breaks the internal filename links. To copy the
large `.fif` file properly, we need to read it and then write with a new file
name. The following command is a shortcut for that:

```bash
qfif <filename_meg.fif> saveas <dst_meg.fif>
```

### Supported file types and configuration

Under the hood, `qfif` relies on file extensions to determine the correct type.
