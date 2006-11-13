# (C) Numbler Llc 2006
# See License For Details.

# custom classes so we can get back to the original string if necessary

class srcfloat(float):
    def __init__(self,strval):
        self.strval = strval
        super(srcfloat,self).__init__(strval)

class srcint(int):
    def __init__(self,strval):
        self.strval = strval
        super(srcint,self).__init__(strval)

class srclong(long):
    def __init(self,strval):
        self.strval = strval
        super(srclong,self).__init__(strval)
