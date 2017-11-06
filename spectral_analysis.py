import sys
import numpy
import dynacode
import Pothos
from scipy import signal
import pickle
#import matplotlib.pyplot as plt

file='/Users/manfeel/Downloads/out.bson'

class SpectralAnalysis(dynacode.DynaProxy):
    def work(self):
        #forward buffer
        if self.input(0).elements():

            in0 = self.input(0).buffer()
            #print(type(in0))
            n = len(in0)
            #print(n)

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
    with open(file, 'rb') as inp:
        data = pickle.load(inp)
    t = data['t']
    f = data['f']
    Sxx = data['Sxx']
    plt.pcolormesh(t, f, Sxx)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()