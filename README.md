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
