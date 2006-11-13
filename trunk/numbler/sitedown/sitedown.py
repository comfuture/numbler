from nevow import loaders,rend,static


# note: this is duplicated from utils.py.  I didn't want
# to have any dependencies on the numbler code base to be able
# to use this tool.

def get_ip_address(ifname):
    """ get the IP address from a named interface.
    useful for getting the IP of eth0, eth0, etc
    """
    
    import socket
    import fcntl
    import struct

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])



class SiteDownPage(rend.Page):
    addSlash = True
    child_logo = static.File('logo.gif')
    docFactory = loaders.xmlfile('sitedown.xml')


    def locateChild(self, ctx, segments):
        return self,()

def createResource():
    return SiteDownPage()


