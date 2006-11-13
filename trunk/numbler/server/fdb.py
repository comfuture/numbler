# (C) Numbler LLC 2006
# See LICENSE for details.

from numbler.server.sslib import singletonmixin

class FDB(dict, singletonmixin.Singleton):
    def __init__(self, *args):
        dict.__init__(self, *args)

