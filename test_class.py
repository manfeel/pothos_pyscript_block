import sys
import numpy
import dynacode

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


class MySwitcher(dynacode.DynaProxy):
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