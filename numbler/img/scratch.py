#!/usr/bin/env python2

##
## Gif animator hack
##

## Away: /usr/local/bin/convert -modulate 40 bud2.png tmp.png
## Depart: fade to dark
## Arrive: flash to white, then settle on fullon
##
## $Id: $
##

import os, sys, math, string

#sourcepath = " /usr/local/share/pybuds/pixmaps/"
sourcepath = " "

def execute(cmd):
    print cmd
    os.system(cmd)
    
def cycle(count, scale):
    increment = math.pi / count
    return map(lambda x: math.sin(x * increment) * scale, range(count))


def superBlur(src, fn):
    out = 0
    for x in cycle(30, 10):
        execute("composite -dissolve %d" % (x * 10) + "% " + src + srcpath + "white.png tmp1.png.%0.2d" % (out))
        # execute("convert -modulate %d %s tmp1.png.%0.2d" % (100 + x * 40, src, out))
        execute("convert -blur %dx%d tmp1.png.%0.2d tmp2.png.%0.2d" % (x * 1.5 + 1, x * 1.5 + 1, out, out))
        # execute("convert -level %d tmp1.png.%0.2d tmp2.png.%0.2d" % (200, out, out))
        # execute("convert -rotate %d tmp1.png.%0.2d tmp2.png.%0.2d" % (x * 5, out, out))
        execute("composite -dissolve %d" % (50 + x) + "% " + src + " tmp2.png.%0.2d out.png.%0.2d" % (out, out))
        out += 1


def superBlur2(src, fn):
    out = 0
    for x in cycle(20, 10):
        execute("convert -blur %dx%d %s tmp1.png.%0.2d" % (x + 1, x + 1, src, out))
        execute("composite -dissolve %d" % (x * 3) + "% " + sourcepath + "white.png tmp1.png.%0.2d tmp2.png.%0.2d" % (out, out))
        execute("composite -dissolve %d" % (30 + x * 6) + "% " + "tmp2.png.%0.2d %s out.png.%0.2d" % (out, src, out))
        out += 1

    execute("convert -delay 10 out.png.* " + fn)
    execute("rm tmp?.png.*")
    execute("rm out.png.*")



## like superblur2, but reuses images -- same effect, half the work
def superBlur3(src,mask, fn):
    out = 0
    for x in cycle(20, 10)[:10]:
        execute("convert -blur %dx%d %s tmp1.png.%0.2d" % (x + 1, x + 1, src, out))
        execute("composite -dissolve %d" % (x * 8) + "% " + sourcepath + mask + " tmp1.png.%0.2d tmp2.png.%0.2d" % (out, out))
        execute("composite -dissolve %d" % (30 + x * 6) + "% " + "tmp2.png.%0.2d %s out.png.%0.2d" % (out, src, out))
        out += 1

    execute("convert -delay 10 " +
            string.join(map(lambda x: "out.png.%0.2d" % x, range(10))) + " " +
            string.join(map(lambda x: "out.png.%0.2d" % x, range(9, -1, -1))) + " " +
            fn)
    execute("rm tmp?.png.*")
    execute("rm out.png.*")
    #execute("rm " + fn + "-*")


def arrowGlow(src, fn):
    out = 0
    for x in cycle(20, 10)[:10]:
        execute("composite -dissolve %d" % (x * 3) + "% " + sourcepath + "white.png %s out.png.%0.2d" % (src, out))
        out += 1

    execute("convert -delay 10 " +
            string.join(map(lambda x: "out.png.%0.2d" % x, range(10))) + " " +
            string.join(map(lambda x: "out.png.%0.2d" % x, range(9, -1, -1))) + " " +
            fn)
    execute("rm out.png.*")

def depart(src, fn):
    out = 0
    for x in range(0, 11):
        # execute("convert -modulate %d,%d %s out.png.%0.2d" % (50 + x * 5, 50 + x * 5, src, out))
        execute("composite -dissolve %d" % (x * 5) + "% " + sourcepath + "black.png %s out.png.%0.2d" % (src, out))
        out += 1

    execute("convert -delay 10 -loop 1 out.png.* " + fn)
    execute("rm out.png.*")

def dim(src, fn):
    execute("composite -dissolve 50% " + sourcepath + "black.png " + src + " " + fn)

def sel(src, fn):
    execute("convert -crop 30x30+1+1 " + src + " -bordercolor grey80 -border 1x1 " + fn)

def seldim(src, fn):
    execute("composite -dissolve 50% " + sourcepath + "black.png " + src + " out.png")
    execute("convert -crop 30x30+1+1 out.png -bordercolor grey80 -border 1x1 " + fn)
    execute("rm out.png")

def arrive(src, fn):
    out = 0
    for x in range(0, 10):
        execute("composite -dissolve %d" % (50 - x * 5) + "% " + sourcepath + "black.png %s out.png.%0.2d" % (src, out))
        out += 1

    # for x in range(0, 10, 2) + range(10, -2, -2):
    for x in range(0, 12, 2):
        execute("composite -dissolve %d " + sourcepath + "white.png " % (x * 10) + "% " + src + " out.png.%0.2d" % (out))
        out += 1

    execute("convert -delay 10 -loop 1 out.png.* out.png.14 out.png.13 out.png.11 out.png.10 " + fn)
    execute("rm out.png.*")


def animate(src, base):
    superBlur3(src, base + "_glo.gif")
    depart(src, base + "_dep.gif")
    arrive(src, base + "_arr.gif")
    dim(src, base + "_dim.png")
    # sel(src, base + "_sel.png")
    # seldim(src, base + "_sdm.png")
    
def main():
    
    if len(sys.argv) >= 4:
        superBlur3(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        print 'superBlur requires 3 arguments: sourcefile maskfile outfile'

    #animate(sys.argv[1], "done")
    

    #arrowGlow(sys.argv[1], sys.argv[2])
    #superBlur3(sys.argv[1],
    return

    for x in cycle(30, 10):
        execute("composite -dissolve %d" % (x * 10) + "% " + src + sourcepath + "white.png out.png.%0.2d" % (out))

        # execute("convert -modulate %d %s tmp1.png.%0.2d" % (100 + x * 40, src, out))

        # execute("convert -gaussian %dx%d -modulate %d %s tmp1.png.%0.2d" % (x * 1.5 + 1, x * 1.5 + 1, 100 + x * 10, src, out))
        # execute("convert -level %d tmp1.png.%0.2d tmp2.png.%0.2d" % (200, out, out))
        # execute("convert -rotate %d tmp1.png.%0.2d tmp2.png.%0.2d" % (x * 5, out, out))
        # execute("composite -dissolve %d" % (50 + x) + "% " + src + " tmp2.png.%0.2d out.png.%0.2d" % (out, out))

        # execute("convert -gaussian %dx%d -modulate %d %s tmp1.%0.2d.ppm" % (x * 1.5 + 1, x * 1.5 + 1, 100 + x * 10, src, out))
        # execute("pnmrotate %d tmp1.%0.2d.ppm >tmp2.ppm.%0.2d" % (x * 10, out, out))
        # execute("composite -dissolve %d" % (50 + x) + "% " + src + " tmp2.ppm.%0.2d out.png.%0.2d" % (out, out))

        out += 1


if __name__ == '__main__': main()

