#!/usr/bin/python

# script to output dtmf digit string
# as a PCM sequence, with 8000Hz sampling, 8-bit quantisation
# to an AU or WAV file

import sys
import os
import struct
import argparse
from math import pi, sqrt, cos
import audio


################################
#                              #
#  dtmfout(dtmf, fname)        #
#                              #
################################

def dtmfout(dtmf, fname):
    # aliases for the non-numeric keys
    STAR = 10
    HASH = 11

    # DTMF frequencies, indexed by the digit
    hi_freq = [1336, 1209, 1336, 1477, 1209, 1336, 1477, 1209, 1336, 1477, 1209, 1477]
    lo_freq = [941, 697, 697, 697, 770, 770, 770, 852, 852, 852, 941, 941]

    # power levels: lo_freq group has -3dB relative to hi_freq group
    # going to use sqrt() from math which is probably overkill
    # could have approximated with 0.707
    hi_pwr = 1
    lo_pwr = 1 / sqrt(2)

    # sampling rate and period
    Fs = 8000
    dt = 1 / float(Fs)

    # define the number of samples for silence (100ms) and dtmf digit (200ms)
    # silence will be added before and after each dtmf digit ie. total 200ms
    n_silence = int(0.1 * Fs)
    n_dtmf = int(0.2 * Fs)
    silence = [0] * n_silence

    # signal will be the final output
    signal = []

    for n in range(len(dtmf)):
        ch = ord(dtmf[n])

        if ch >= ord('0') and ch <= ord('9'):
            # numeric keys
            fhi = hi_freq[ch - ord('0')]
            flo = lo_freq[ch - ord('0')]
        elif dtmf[n] == '*':
            fhi = hi_freq[STAR]
            flo = lo_freq[STAR]
        elif dtmf[n] == '#':
            fhi = hi_freq[HASH]
            flo = lo_freq[HASH]
        else:
            # silently drop invalid characters
            continue

        dig = [0] * n_dtmf
        for m in range(n_dtmf):
            dig[m] = int((hi_pwr * cos(2 * pi * fhi * m * dt) +
                          lo_pwr * cos(2 * pi * flo * m * dt)) * 64)

        signal = signal + silence + dig + silence

    return audio.write(fname, audio.TYPE_AU, signal, Fs)


################################
#                              #
#  main()                      #
#                              #
################################

# instantiate an argument parser
parser = argparse.ArgumentParser(
    description = "Generate an audible DTMF sequence as an AU or WAV file.\
    Valid digits are 0-9, *, #. Invalid characters are silently discarded,\
    but if there are no valid characters in the string an error message is displayed")

# add a positional argument for the digit sequence
parser.add_argument("dtmf", help="DTMF digit sequence")

# group for mutually exclusive arguments for file type
group = parser.add_mutually_exclusive_group()
group.add_argument("-au", dest="file", help="output au file")
group.add_argument("-wav", dest="file", help="output wav file")


# parse the arguments
args = parser.parse_args()

# output filename is guaranteed to be defined
err = dtmfout(args.dtmf, args.file)

if err != 0:
    sys.stderr.write(parser.prog + ": " + os.strerror(err) + "\n")


