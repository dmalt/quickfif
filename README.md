Tools to preview `.fif` files (raw data, epochs, annotations, ica solutions)
info from terminal, inspect them in ipython console and more.
Ready for integration with CLI-based file managers, such as
[ranger](https://github.com/ranger/ranger).


Quickstart
==========

To install the tools, run

```bash
python3 -m pip install --user pipx
pipx install git+https://github.com/ranger/ranger.git
```

The `mct` command should now be available in the terminal.

To preview the file, run

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
