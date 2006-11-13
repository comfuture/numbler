#!/usr/bin/env python
# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
#
# generate the compressed dojo file.

from subprocess import *
import os
import shutil

from optparse import OptionParser

builddir = "dojo/buildscripts"
profiledir = builddir + '/profiles/'

def generateDojo(customprofile,outfile):

    open(profiledir + customprofile,'w').write(open(customprofile,'r').read())
    
    p = Popen(['java','-jar','lib/custom_rhino.jar','-e',"load('profiles/%s')" % (customprofile)],
              stdout=PIPE,cwd=builddir)
    deps = p.communicate()[0]
    files = deps.replace('\n','').replace('..','dojo').split(',')
    tmpname = os.tmpnam()
    tfp = open(tmpname,'w')
    for item in files:
        tfp.write(open(item).read())
    tfp.close()
    
    p = Popen(['java','-jar','lib/custom_rhino.jar','-c',tmpname],stdout=PIPE,cwd=builddir)
    dfp = open(outfile,'w')
    dfp.write(open('dojo/buildscripts/build_notice.txt').read())
    shutil.copyfileobj(p.stdout,dfp)
    dfp.flush()
    dfp.close()
    os.unlink(tmpname)



def main():
    parser = OptionParser()
    parser.add_option("-s","--small",action="store_true",dest="small")
    parser.add_option("-f","--full",action="store_true",dest="full")

    (options,args) = parser.parse_args()
    if options.small:
        generateDojo('smalldojo.js','dojo/smallcompressed.js')
    elif options.full:
        generateDojo('mydojoprofile.js','dojo/compresseddojo.js')
    else:
        print 'either -s or -f required'

    
if __name__ == '__main__': main()
