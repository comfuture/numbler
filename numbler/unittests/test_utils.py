#
from testtools import *
from numbler.server.sslib.utils import guidbin

class testNumblerUtils(unittest.TestCase):

    def testBinGuid(self):
        # ensure that for many iterations of binguid() it doesn't return a value with a trailing space.
        targetlen= 1000
        guidlist = [y for y in [guidbin() for x in xrange(0,targetlen)] if y[-1] != ' ']
        self.failUnless(len(guidlist) == targetlen)
        
