import sys
import numpy

class MyClass:
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


class OtherClass:
    def a1(self):
        pass

    def a2(self):
        pass

