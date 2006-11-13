#! /usr/bin/python
import os, sys, glob, shutil, re, string

def main():
    fdirs = []
    ffiles = []
    for root, dirs, files in list(os.walk('.')):
        ffiles += [os.path.join(root, f) for f in files if f.endswith(".rest")]
        fdirs += [os.path.join(root, d) for d in dirs if (string.find(os.path.join(root, d), r".svn") == -1)]
        
    for source in ffiles:
        (tdir, tfn) = os.path.split(source)
        tdir = os.path.normpath(os.path.join("../jot/", tdir))
        if not os.path.isdir(tdir):
            os.makedirs(tdir)
            
        target = os.path.abspath(
            os.path.join(tdir, os.path.splitext(tfn)[0]+".html.xml")
        )
        build = True
        
        if os.path.isfile(target):
            build = os.lstat(source)[8] > os.lstat(target)[8]
            
        if build:
            print source, target
            os.system("rst2html.py --stylesheet-path=./jot.css  %s %s" % (source, target))

    # print 1/0

    for source in fdirs:
        # we need to construct blank jot nodes in order for the subdir
        # contents to be correctly imported
        source = os.path.normpath(os.path.join("../jot", source+".xml"))
        if not os.path.isfile(source):
            open(source, "w+").write("<html></html>")

    shutil.copy("index.html", os.path.join(tdir, "index.html.xml"))
    # make a zip file suitable for import into Jot
    os.system("cd ../jot && zip -q -r ../manual.jot.zip `find . | grep \\.xml`")

if __name__=="__main__":
    main()

# vim:ts=4:et:shiftwidth=4:
