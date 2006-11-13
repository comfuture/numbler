# (C) Numbler Llc 2006
# See License For Details.

##
## utils
## misc shite for spreadsheet
##

import os, sha, base64, time, socket, string, random, re

def base64sha(text):
    sh = sha.sha()
    sh.update(text)
    return base64.encodestring(sh.digest())[:-1]

## guid built on ip adr, time, random value

nonspace = range(0,31) + range(33,256)

def guidbin():
    val = sha.new(string.join([socket.gethostbyname(socket.gethostname()),
                                  str(time.time()),
                                  str(random.randrange(2**31))], '')).digest()

    # work around for an obscure mysql 4.1x bug: mysql will strip off any
    # blank characters at the end of a string.  We need to enusre that the last
    # value is not a ASCII space.
    if val[-1] == ' ':
        return val[0:-1] + chr(random.choice(nonspace))
    else:
        return val
    #return val


def guid():
    return base64sha(string.join([socket.gethostbyname(socket.gethostname()),
                                  str(time.time()),
                                  str(random.randrange(2**31))], ''))

## 0-9A-Za-z
symbols = map(chr, range(48, 58) + range(65, 91) + range(97, 123))

def guid16():
    # FIXME: better replace randomly occurring nasty words if these
    # are going to be seen by users
    return string.join(map(lambda x: random.choice(symbols), range(16)), '')

alphasym = map(chr,range(65, 91) + range(97, 123))
def alphaguid16():
    return string.join(map(lambda x: random.choice(alphasym), range(16)), '')

def alphaguid20():
    return string.join(map(lambda x: random.choice(alphasym), range(20)), '')

def alphaguid8():
    return string.join(map(lambda x: random.choice(alphasym), range(8)), '')    

def main():
    pass

if __name__ == '__main__': main()
    
