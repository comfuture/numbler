#!/bin/env python

import testtools
import os
from twisted.python.reflect import namedAny
from numbler.server.sslib import flatten

unit_folders = [
    'formulas'

    ]

trial_folders = [
    'trialbased'
    ]


#os.listdir(

suitelist = []

from numbler.server import engine
eng = engine.Engine.getInstance()

for folder in unit_folders:
    contents = os.listdir(folder)
    pyfiles = ['.'.join([folder,x[0]]) for x in [os.path.splitext(x) for x in contents] if x[1] == '.py' and x[0] != '__init__']
    fsuitelist = flatten.flatten([namedAny(x).suitelist for x in pyfiles])
    suitelist += fsuitelist
    print suitelist

# run all these tests
testtools.testmain(suitelist)
    
