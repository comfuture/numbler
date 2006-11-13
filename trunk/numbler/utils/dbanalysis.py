#!/bin/env python

from numbler.server import engine

eng = engine.Engine.getInstance()
import re
from numbler.server.sslib.flatten import flatten

def findUniqueFormulas():
    
    p = re.compile(r'[A-Za-z]+\(')
    # this could take a while
    results = eng.ssdb.rsql("select formula from cell where formula REGEXP '^='")
    return set((x[:-1] for x in (flatten((p.findall(row[0]) for row in results)))))

uniquefx = findUniqueFormulas()
