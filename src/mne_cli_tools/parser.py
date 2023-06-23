from argparse import ArgumentParser


def parse_fname():
    parser = ArgumentParser(description="Open .fif file in ipython console")
    parser.add_argument("path", help="FIF file to open")
    args = parser.parse_args()
    return args.path
