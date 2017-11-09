import sys
import numpy
import dynacode
import Pothos

class MyClass(object):
    def activate(self, pb):
        print(sys._getframe(1).f_code.co_name)
        print(pb.mod)

    def deactivate(self, pb):
        print(sys._getframe(1).f_code.co_name)
        print(pb)

    def work(self, pb):
        inPort = pb.input(0)

        if inPort.hasMessage():
            msg = inPort.popMessage()
            print("Message type is: " + msg.getClassName())
            if msg.getClassName() == 'Pothos::Packet':
                # no need for extract() in python
                #packet = msg.extract()
                buffer = msg.payload
                print("Payload is: " + str(type(buffer)))
                # isinstance could tell the inheritance of a type
                if type(buffer) is numpy.ndarray:
                    buffer = buffer.tobytes()

                print(buffer)

# ref from https://gist.github.com/sbz/1080258
def hexdump(src, length=16):
    is_string = isinstance(src, str)

    def getc(c):
        d = ord(c) if is_string else c
        return d

    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []

    for c in xrange(0, len(src), length):
        chars = src[c:c+length]
        hex = ' '.join(["%02x" % getc(x) for x in chars])
        printable = ''.join(["%s" % ((getc(x) <= 127 and FILTER[getc(x)]) or '.') for x in chars])
        lines.append("%04x  %-*s |  %s\n" % (c, length*3, hex, printable))
    return ''.join(lines)


class ArbitarySignals(dynacode.DynaProxy):
    @dynacode.signal_slot
    def setFloatValue(self, value):
        print(value)

    @dynacode.signal_slot
    def setIntValue(self, value):
        print(value)


class MySwitcher(dynacode.DynaProxy):
    def init(self):
        self.registerSignal('paramChanged')
        self.param = None
        '''
        env = Pothos.ProxyEnvironment("managed")
        e = env.findProxy('Pothos/Util/EvalEnvironment').make()
        #e.registerConstantObj('s', should_be_object)
        r = e.eval('sampRate')
        print('r : {0}'.format(r))
        r = e.eval('s*2')
        print('r : {0}'.format(r))
        '''

    def work(self):
        op = self.param
        #forward buffer
        if self.input(0).elements():
            out0 = self.output(op).buffer()
            in0 = self.input(0).buffer()
            n = min(len(out0), len(in0))

            out0[:n] = in0[:n]
            self.input(0).consume(n)
            self.output(op).produce(n)

    def activate(self):
        print('WoW, activate called!')

    def deactivate(self):
        print('WoW, deactivate called!')
        self.paramChanged('end')

    @dynacode.signal_slot
    def setDynamicParam(self, param):
        print('param is {0}, value={1}'.format(type(param), param))
        self.param = param