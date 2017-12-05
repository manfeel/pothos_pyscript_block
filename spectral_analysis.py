import sys
import numpy as np
import dynacode
import Pothos
from scipy import signal
import pickle
import os
#import matplotlib.pyplot as plt

file='/Users/manfeel/Downloads/out.bson'

class fft_record(dynacode.DynaProxy):
    def init(self):
        # set default sample rate
        self.sampRate = 10e6

    @dynacode.signal_slot
    def setSampRate(self, sampRate):
        self.sampRate = sampRate

    def activate(self):
        self.sampRate = self.globals['s']

    def work(self):
        n = self.input(0).elements()
        #print(n)
        if n < 1024:
            return

        try:
            in0 = self.input(0).buffer()
            out = self.output(0).buffer()
            n = min(len(in0), len(out))
            rst = np.fft.fft(in0)
            Lo = 50e3
            Hi = 250e3
            l = len(rst)
            for i in range(l):
                #print("rst[%d]=%s" % (i, str(rst[i])))
                if i<int(l*Lo/self.sampRate) or i > int(l*Hi/self.sampRate): rst[i]=0

            irst = np.fft.ifft(rst)
            out[:n] = irst[:n]
            self.input(0).consume(n)
            self.output(0).produce(n)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)



class SpectralAnalysis(dynacode.DynaProxy):
    def work(self):
        #forward buffer
        if self.input(0).elements():

            in0 = self.input(0).buffer()
            #print(type(in0))
            n = len(in0)
            #print(n)

            r = np.fft.fft(in0)
            # deal spectrogram
            f, t, Sxx = signal.spectrogram(in0, 10e6)
            data = {}
            data['f'] = f
            data['t'] = t
            data['Sxx'] = Sxx
            with open(file, 'wb') as out:
                print('begin write')
                pickle.dump(data, out)
                print('write end')
            #print('sxx={0},f={1},t={2}'.format(Sxx, f, t))
            '''
            plt.pcolormesh(t, f, Sxx)
            plt.ylabel('Frequency [Hz]')
            plt.xlabel('Time [sec]')
            plt.show()
            '''
            self.input(0).consume(n)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    with open('/Users/manfeel/Downloads/sig.bin', 'rb') as inp:
        data = pickle.load(inp)
    t = data['t']
    f = data['f']
    Sxx = data['Sxx']
    plt.pcolormesh(t, f, Sxx)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()
