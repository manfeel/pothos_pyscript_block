# pothos_pyscript_block
A pothos block that can execute dynamic python script!
# simple to use
```
import dynacode

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
```