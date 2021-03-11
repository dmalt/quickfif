import mne
from argparse import ArgumentParser
import IPython

parser = ArgumentParser(description="Open .fif file in ipython console")
parser.add_argument("path", help="FIF file to open")
args = parser.parse_args()

fname = args.path

if fname.endswith("epo.fif"):
    epo = mne.read_epochs(fname, verbose="ERROR")
    header = "Read mne-python epochs into `epo`."
else:
    raw = mne.io.Raw(fname, verbose="ERROR")
    header = "Read mne-python raw into `raw`."

IPython.embed(colors="neutral", header=header)
