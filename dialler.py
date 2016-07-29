#!/usr/bin/python

from math import pi, sqrt, cos
from Tkinter import *
import ossaudiodev

STAR = 10
HASH = 11

class Dialler(Frame):
    snd = None
    Fs = 8000
    zeroLevel = 127

    def dtmfout(self, x):
        # DTMF frequencies, indexed by the digit
        hi_freq = [1336, 1209, 1336, 1477, 1209, 1336, 1477, 1209, 1336, 1477, 1209, 1477]
        lo_freq = [941, 697, 697, 697, 770, 770, 770, 852, 852, 852, 941, 941]

        # power levels: lo_freq group has -3dB relative to hi_freq group
        hi_pwr = 0.25
        lo_pwr = hi_pwr / sqrt(2)

        # define the number of samples for silence (100ms) and dtmf digit (200ms)
        # silence will be added before and after each dtmf digit ie. total 200ms
        n_silence = int(0.1 * self.Fs)
        n_dtmf = int(0.2 * self.Fs)
        silence = [self.zeroLevel] * n_silence

        fhi = hi_freq[x]
        flo = lo_freq[x]

        digit = [0] * n_dtmf
        # need to add a dc component so that values are unsigned
        for n in range(n_dtmf):
            digit[n] = int((hi_pwr * cos(2 * pi * fhi * n / self.Fs) +
                            lo_pwr * cos(2 * pi * flo * n / self.Fs)) * 64) + self.zeroLevel

        signal = silence + digit + silence

        # now create the string from the list of integers for audio output
        s = str(bytearray(signal))
        self.snd.write(s)

    def quit():
        self.snd.close()
        sys.exit()

    def createWidgets(self):
        self.digit = [None] * 12
        for n in range(10):
            self.digit[n] = Button(self, text=str(n), command=(lambda X=n: self.dtmfout(X)))

        # define digits STAR and HASH
        self.digit[STAR] = Button(self, text='*', command=(lambda X=STAR: self.dtmfout(X)))
        self.digit[HASH] = Button(self, text='#', command=(lambda X=HASH: self.dtmfout(X)))

        self.digit[1].grid(row=0, column=0)
        self.digit[2].grid(row=0, column=1)
        self.digit[3].grid(row=0, column=2)
        self.digit[4].grid(row=1, column=0)
        self.digit[5].grid(row=1, column=1)
        self.digit[6].grid(row=1, column=2)
        self.digit[7].grid(row=2, column=0)
        self.digit[8].grid(row=2, column=1)
        self.digit[9].grid(row=2, column=2)
        self.digit[STAR].grid(row=3, column=0)
        self.digit[0].grid(row=3, column=1)
        self.digit[HASH].grid(row=3, column=2)

        self.quitButton = Button(self, text='Quit', command=quit)
        self.quitButton.grid(row=4, column=1)


    def __init__(self, master=None):
        self.snd = ossaudiodev.open('/dev/audio', 'w')
        self.snd.setparameters(ossaudiodev.AFMT_U8, 1, self.Fs)

        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()


root = Tk()
app = Dialler(master=root)
app.mainloop()
root.destroy()

