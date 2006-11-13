# (C) Numbler Llc 2006
# See License For Details.


##
## handle.py
##
## Base class for Handles
##

import weakref


class OneOfSeveral(object):
    """
    class maintains weak dict of refs to all instances.
    instantiation returns existing instance if available
    """
    
    _instances = weakref.WeakValueDictionary()

    def argsToKey(cls, *args):
        # Implement this. Generate unique key from arguments
        raise NotImplementedError
    argsToKey = classmethod(argsToKey)
    
    def getInstance(cls, *args):
        key = cls.argsToKey(*args)
        if key in cls._instances:
            return cls._instances[key]
        instance = cls(*args)
        cls._instances[key] = instance
        return instance
    getInstance = classmethod(getInstance)


class Handle(object):

    _handles = weakref.WeakValueDictionary()
    # set _Obj in derived class to the class this is to be a handle for
    # _Obj = FooClass
    _Obj = None

    def argsToKey(cls, *args):
        # Implement this. Generate unique key from arguments
        raise NotImplementedError
    
    def getInstance(cls, *args):
        key = cls.argsToKey(*args)
        if key in cls._handles:
            return cls._handles[key]
        handle = cls(*args)
        cls._handles[key] = handle
        return handle
    getInstance = classmethod(getInstance)

    def __init__(self):
        self._obj = None

    def __call__(self):
        """shorthand to return my referred object"""
        if self._obj == None or self._obj() == None:
            self._obj = weakref.ref(self._Obj.getInstanceFromHandle(self))
        return self._obj()

    def purge(cls):
        cls._handles = weakref.WeakValueDictionary()
    purge = classmethod(purge)
