# dtmf

Script to generate an audible DTMF sequence as an AU or WAV file.
Valid digits are 0-9, *, #. Invalid characters are silently discarded,
but if there are no valid characters in the string an error message is displayed

<code>
usage: dtmf.py [-h] [-au FILE | -wav FILE] dtmf

positional arguments:
  dtmf        DTMF digit sequence

optional arguments:
  -h, --help  show this help message and exit
  -au FILE    output au file
  -wav FILE   output wav file
</code>
