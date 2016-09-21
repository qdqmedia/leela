import importlib

def import_from_module(path):
    """Imports a function/class from a module, given its path"""
    modulepath = ('.').join(path.split('.')[:-1])
    obj_name = path.split('.')[-1]
    module = importlib.import_module(modulepath)
    return module.__getattribute__(obj_name)
