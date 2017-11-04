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


def import_file(fpath):
    """
    fpath - the relative or absolute path to the .py file which is imported.

    Returns the imported module.

    NOTE: if import_file is called twice with the same module, the module is reloaded.
    """
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

filter_method = ['work', 'activate', 'deactivate', 'propagateLabels']
#dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i not in set(y) ])

class DynaProxy(object):
    """
    Proxy class for dynamic subclass init the `self' var to parent.self var.
    """
    def __init__(self, dynacode_self):
        self.refClass = dynacode_self

    def __getattr__(self, name):
        #print('getattr : {0}'.format(name))
        return getattr(self.refClass, name)


class Dynacode(Pothos.Block):
    def __init__(self, dtype, inChans, outChans):
        Pothos.Block.__init__(self)
        # setup input channels
        for i in range(inChans):
            self.setupInput(i, dtype)
        # setup output channels
        for i in range(outChans):
            self.setupOutput(i, dtype)
        self.registerSlot('setDynamicParam')
        # init instance var
        self.mod = None
        self.clz = None
        self.bindcls = None
        self.param = None

    def setDynamicParam(self, param):
        print('param is {0}, value={1}'.format(type(param), param))
        self.param = param

    def loadScript(self, pspath):
        self.mod = import_file(pspath)
        print('{0} has been loaded'.format(self.mod))
        self.clz = inspect.getmembers(self.mod, inspect.isclass)
        #print(self.clz)

    def getClassByName(self, className):
        for k, v in self.clz:
            if k == className:
                return v
        return None

    def bindClass(self, className):
        #print('bind class name: ' + className)
        for key, val in self.clz:
            if key == className:
                cc = self.getClassByName(className)
                if not issubclass(cc, DynaProxy):
                    print('ERROR: {0} is not a subclass of {1}!'.format(cc, DynaProxy))
                    return

                self.bindcls = cc(self)

                # bind some method
                for m in filter_method:
                    if hasattr(self.bindcls, m):
                        setattr(self, m, getattr(self.bindcls, m, None))
                return

        print('ERROR: class "{0}" has Nothing to bind!'.format(className))

    # call the same method in script
    def checkAndCall(self):
        # get the func name of caller
        # sys._getframe().f_code.co_name will return the own func name
        parentFunc = sys._getframe(1).f_code.co_name
        op = getattr(self.bindcls, parentFunc, None)
        if callable(op):
            op()

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