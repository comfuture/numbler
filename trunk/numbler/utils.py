# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from twisted.internet import defer,reactor
import re

def yieldDef():
    d = defer.Deferred()
    reactor.callLater(0,d.callback,None)
    return d

def cellDepFlattener(deps):
    """ flatten two deep array"""
    for dep in deps:
        for singledep in dep:
            yield singledep




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
    

# simple class for populating from a dictionary 
class simplecell:
    def __init__(self,dict,boundingCol = 0,boundingRow = 0):
        self.row = int(dict['row'])
        self.col = int(dict['col'])
        self.formula = dict['formula']
        if dict.has_key('text'):
            self.text = dict['text']
        else:
            self.text = ''
        if boundingCol >0  and boundingRow > 0:
            self.offset_col = self.col - boundingCol
            self.offset_row = self.row - boundingRow
        else:
            self.offset_col = 0
            self.offset_row = 0

        custom = dict.get('customStyle') or None
        self.format = custom and custom.get('cache') or None

    def getValue(self):
        if self.formula != '':
            return self.formula
        else:
            return self.text



def remove_whitespace_nodes(node, unlink=False):
    """Removes all of the whitespace-only text decendants of a DOM node.
    
    When creating a DOM from an XML source, XML parsers are required to
    consider several conditions when deciding whether to include
    whitespace-only text nodes. This function ignores all of those
    conditions and removes all whitespace-only text decendants of the
    specified node. If the unlink flag is specified, the removed text
    nodes are unlinked so that their storage can be reclaimed. If the
    specified node is a whitespace-only text node then it is left
    unmodified."""

    from xml import dom
    
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == dom.Node.TEXT_NODE and \
           not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whitespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()

# validate email addresses (sort of)
emailRegex = re.compile(r'^[a-zA-Z0-9._%-]+@(?P<domainname>[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})$')        

def validEmail(testval):
    return emailRegex.match(testval)
