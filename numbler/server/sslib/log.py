# (C) Numbler Llc 2006
# See License For Details.

##
## log.  Better than bad, it's good.
##

import time, sys
import singletonmixin

##
## Logfile utility
##

class Log(singletonmixin.Singleton):

    def __init__(self, file):
        """file is either a string logfilename or an open file handle or other object
        that behaves like an open file"""
        
        if type(file) == str:
            self.file = open(file, "a")
        else:
            # Assume it is an objec that supports write() and flush()
            self.file = file

        self.quiet = False

    def setDebug(debug):
        self._debug = debug

    def __call__(self, *logstrs):
        return self.log(*logstrs)

    def _getTime(self):
        tm = time.time()
        return time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(tm)) + ":%.2d" % int((tm - int(tm)) * 100) + " "

    def log(self, *logstrs):
        if self.quiet: return
        self.file.write(self._getTime() + " ".join(map(str, logstrs)) + '\n')
        self.file.flush()

    ## 
    ## loglevels:
    ##   DEBUG    (only logged if self._debug == True)
    ##   INFO
    ##   WARNING
    ##   ERROR
    ##

    def debug(self, *logstrs):
        if self._debug: self.log("DEBUG", *logstrs)
    def info(self, *logstrs): self.log("INFO", *logstrs)
    def warning(self, *logstrs): self.log("WARNING", *logstrs)
    def error(self, *logstrs): self.log("ERROR", *logstrs)

def log(fn = sys.stdout):
    return Log.getInstance(fn)

def main():
    log = Log.getInstance(sys.stdout)
    log("test", "dick")
    log.error("test", "dick")

if __name__ == '__main__': main()
