import Pothos
import imp as _imp
import os as _os
import sys
import json
import inspect
"""/*
|PothosDoc DynaScript

Dynamic load and run a python script from file.

|category /Misc
|keyword dnyacode

|param dtype[Data Type] The data type
|option [Complex Float32] "complex_float32"
|option [Float32] "float32"
|option [Int32] "int32"
|option [Int16] "int16"
|option [Int8] "int8"
|option [UInt8] "uint8"
|default "float32"

|param inChans [Num input Channels] The number of input channels.
This parameter controls the number of input channels.
|widget SpinBox(minimum=1)
|default 1
|preview disable

|param outChans [Num output Channels] The number of output channels.
This parameter controls the number of output channels.
|widget SpinBox(minimum=1)
|default 1
|preview disable

|param pspath[Python script file Path] The path to the output file.
|default ""
|widget FileEntry(mode=open)
|preview disable

|param className[Bind Class] The class name of the load script,
or an empty string to use the first class.
|widget ComboBox(editable=false)
|default ""
|preview valid

|factory /blocks/dynacode(dtype, inChans, outChans)
|initializer loadScript(pspath)
|initializer bindClass(className)
*/"""


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


def import_file(fpath):
    '''
    fpath - the relative or absolute path to the .py file which is imported.

    Returns the imported module.

    NOTE: if import_file is called twice with the same module, the module is reloaded.
    '''
    if hasattr(_os, 'getcwdu'):
        # python 2 returns question marks in os.path.realpath for
        # ascii input (eg '.').
        original_path = _os.path.realpath(_os.getcwdu())
    else:
        original_path = _os.path.realpath(_os.path.curdir)
    dst_path = _os.path.dirname(fpath)
    if dst_path == '':
        dst_path = '.'

    # remove the .py suffix
    script_name = _os.path.basename(fpath)
    if script_name.endswith('.py'):
        mod_name = script_name[:-3]
    else:
        # packages for example.
        mod_name = script_name

    _os.chdir(dst_path)
    fhandle = None
    try:
        tup = _imp.find_module(mod_name, ['.'])
        module = _imp.load_module(mod_name, *tup)
        fhandle = tup[0]
    finally:
        _os.chdir(original_path)
        if fhandle is not None:
            fhandle.close()

    return module


class dynacode(Pothos.Block):
    def __init__(self, dtype, inChans, outChans):
        Pothos.Block.__init__(self)
        #setup input channels
        for i in range(inChans):
            self.setupInput(i, dtype)
        #setup output channels
        for i in range(outChans):
            self.setupOutput(i, dtype)
        self.bindcls = None

    def setTitle(self, title):
        pass

    def loadScript(self, pspath):
        self.mod = import_file(pspath)
        print('{0} has been loaded'.format(self.mod))
        self.clz = inspect.getmembers(self.mod, inspect.isclass)
        print(self.clz)

    def bindClass(self, className):
        print('bind class name: ' + className)
        for key, val in self.clz:
            if key == className:
                self.bindcls = val()
                return;
        print('Nothing to bind!')

    # call the same method in script
    def checkAndCall(self):
        # get the func name of caller
        # sys._getframe().f_code.co_name will return the own func name
        parentFunc = sys._getframe(1).f_code.co_name
        op = getattr(self.bindcls, parentFunc, None)
        if callable(op):
            op(self)

    # json overlay
    def overlay(self):
        js = {"params": [{
            "key": "className",
            "options": [
                {"name": "None", "value": "\"\""}
            ],
            "widgetKwargs": {
                "editable": False
            },
            "widgetType": "ComboBox"
            }]
        }

        opts = js['params'][0]['options']
        for key, val in self.clz:
            # must enclosed with double quotation
            v = '"'+ key + '"'
            opts.append({'name': key, 'value':v})
        #print(opts)
        v = json.dumps(js)
        #print(v)
        return v

    def activate(self):
        #print('activate')
        self.checkAndCall()

    def deactivate(self):
        #print('deactivate')
        self.checkAndCall()

    def work(self):
        self.checkAndCall()
