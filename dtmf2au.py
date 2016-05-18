#!/usr/bin/python

# $Id: dtmf2au.py,v 1.0 2016/05/12 06:46:41 cbl Exp $
#
# script to output dtmf digit string
# as a PCM sequence, with 8000Hz sampling, 8-bit quantisation
# to an AU file

import sys
import struct
import argparse
from math import pi, sqrt, cos


################################
#                              #
#  dtmf2au(dtmf, fname)        #
#                              #
################################

def dtmf2au(dtmf, fname):
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
    lo_pwr = 1/sqrt(2)

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


    #
    # output
    #
    magic    = ".snd"
    offset   = 0x18           # bare minimum header
    size     = len(signal)
    codec    = 0x02           # linear PCM
    channels = 0x01           # mono channel

    # if no valid dtmf chars, just exit
    if len(signal) == 0:
        return None

    # try writing the AU header to the output file
    try:
        aufile = open(fname, 'wb')
        aufile.write(magic)
        aufile.write(struct.pack(">I", offset))
        aufile.write(struct.pack(">I", size))
        aufile.write(struct.pack(">I", codec))
        aufile.write(struct.pack(">I", Fs))
        aufile.write(struct.pack(">I", channels))

        # construct a format string to say that we have /size/ bytes
        fmt = "%db" % size
        aufile.write(struct.pack(fmt, *signal))
    except IOError:
        return -1

    # no error
    aufile.close
    return 0


################################
#                              #
#  main()                      #
#                              #
################################

# instantiate an argument parser
parser = argparse.ArgumentParser(description="Generate an audible DTMF sequence as a Sun audio file. Valid digits are 0-9, *, #")

# add a positional argument for the digit sequence
parser.add_argument("dtmf", help="DTMF digit sequence")

# add an mandatory argument for the output filename
parser.add_argument("-o", "--output", dest="file", required=True, help="output file")


# parse the arguments
args = parser.parse_args()

# output filename is guaranteed to be defined
# print "will write sequence '%s' to %s" % (args.dtmf, args.file)
err = dtmf2au(args.dtmf, args.file)

if err is None:
    sys.stderr.write("No valid DTMF characters\n")
elif err == -1:
    sys.stderr.write("Could not write to output file %s\n" % args.file)



