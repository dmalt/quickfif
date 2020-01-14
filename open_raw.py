import mne
import sys

raw_fname = sys.argv[1]

raw = mne.io.Raw(raw_fname, verbose="ERROR")
