#!/usr/bin/env python

from numbler.unittests.testtools import *

class countTestCase(formulaTestCase):
    """
    test basic boolean functionality
    """

    def testCountNumbers(self):
        pass

    def testCountSkipsNonNumbers(self):
        pass

    
    

class countATestCase(formulaTestCase):

    def testCountNonEmptyCells(self):
        pass
    
    
suitelist = [countTestCase,countATestCase]


if __name__ == '__main__': testmain(suitelist)
