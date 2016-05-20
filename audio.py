#!/usr/bin/python

import struct
import errno

# define some values for general use
TYPE_AU  = 1
TYPE_WAV = 2


def auheader(aufile, Fs, size):
    magic    = ".snd"
    offset   = 0x18           # bare minimum header
    codec    = 0x02           # linear PCM
    channels = 0x01           # mono channel

    # try writing the AU header to the output file
    try:
        aufile.write(magic)
        aufile.write(struct.pack(">I", offset))
        aufile.write(struct.pack(">I", size))
        aufile.write(struct.pack(">I", codec))
        aufile.write(struct.pack(">I", Fs))
        aufile.write(struct.pack(">I", channels))
    except IOError as e:
        return e.errno

    return 0


def wavheader(wavfile, Fs, size):
    #
    # WAV header fields
    #

    riff = "RIFF"
    riff_len = size + 36

    wave = "WAVE"

    fmt = "fmt "
    fmt_len = 16      # fixed for linear PCM, no extra parameters
    codec = 0x0001    # linear PCM
    channels = 1
    sample_rate = Fs
    bits_per_sample = 8
    byte_rate = sample_rate * channels * bits_per_sample
    block_align = channels * bits_per_sample / 8

    data = "data"
    

    # try writing the WAV header to the output file
    try:
        wavfile.write(riff)
        wavfile.write(struct.pack("<I", riff_len))

        wavfile.write(wave)

        wavfile.write(fmt)
        wavfile.write(struct.pack("<I", fmt_len))
        wavfile.write(struct.pack("<H", codec))
        wavfile.write(struct.pack("<H", channels))
        wavfile.write(struct.pack("<I", sample_rate))
        wavfile.write(struct.pack("<I", byte_rate))
        wavfile.write(struct.pack("<H", block_align))
        wavfile.write(struct.pack("<H", bits_per_sample))

        wavfile.write(data)
        wavfile.write(struct.pack("<I", size))
    except IOError as e:
        return e.errno

    return 0


def write(fname, ftype, signal, Fs):
    # this function determines the type of audio file requested
    # and calls the appropriate header writing function
    # then writes the samples into the file
    #
    # return value: 0 if ok, errno otherwise

    #
    # validate that signal is list of integers in range [-128:127]
    #
    if type(signal) is not list:
        return errno.EINVAL

    size = len(signal)
    if size == 0:
        return errno.EINVAL

    for n in range(size):
        if type(signal[n]) is not int or signal[n] < -128 or signal[n] > 127:
            return errno.EINVAL


    # try opening the file for writing
    try:
        fh = open(fname, 'wb')
    except IOError as e:
        return e.errno

    #
    # check that the file type is valid and call the appropriate
    # function to write the header
    #
    if ftype == TYPE_AU:
        err = auheader(fh, Fs, size)
    elif ftype == TYPE_WAV:
        err = wavheader(fh, Fs, size)
    else:
        return errno.EINVAL

    # an error has been returned from the header function
    if err != 0:
        return err

    # construct a format string to say that we have /size/ bytes
    # and then write to the file handle
    fmt = "%db" % size
    try:
        fh.write(struct.pack(fmt, *signal))
        fh.close()
    except IOError as e:
        return e.errno

    return 0

