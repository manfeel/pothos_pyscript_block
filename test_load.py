import imp as _imp
import os as _os
import json
import inspect
import sys

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

    # json overlay
def overlay(clz):
    print sys._getframe(1).f_code.co_name
    #print("overlay has been called")
    js = {"params": [{
        "key": "className",
        "options": [],
        "widgetKwargs": {
            "editable": False
        },
        "widgetType": "ComboBox"
        }]
    }

    opts = js['params'][0]['options']
    for key, val in clz:
        opts.append({'name':key, 'value':key})
    print(opts)
    v = json.dumps(js)
    print(v)
    return v

def wrap(clz):
    return overlay(clz)

class dynacode:
    def __init__(self):
        self.bindcls = None

    def loadScript(self, pspath):
        self.mod = import_file(pspath)
        print('{0} has been loaded'.format(self.mod))
        self.clz = inspect.getmembers(self.mod, inspect.isclass)
        print(self.clz)

    def bindClass(self, className):
        print(className)
        for key, val in self.clz:
            if key == className:
                self.bindcls = val()
                return;
        print('Nothing bind!')

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
        pass

    def activate(self):
        self.checkAndCall()

    def deactivate(self):
        self.checkAndCall()

    def work(self):
        self.checkAndCall()


if __name__ == '__main__':
    c = dynacode()
    c.loadScript('/Users/manfeel/PycharmProjects/pothos_pyscript_block/test_class.py')
    print(c.clz)
    c.bindClass('MyClass')
    c.activate()
    c.deactivate()