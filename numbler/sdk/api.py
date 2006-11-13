#!/usr/bin/env python
#
# (C) Numbler LLC 2006
# See LICENSE for details.
# 


import sha,hmac,time,httplib,base64,StringIO,urllib
from xml.dom.minidom import parseString 
from xml.sax.saxutils import XMLGenerator

default_server = "ws.numbler.com"
default_port = 80


def translatecol(col):
    v = col -1
    a = v / 26
    return "%s%s" % (a and chr(a+96) or "",chr(v % 26 + 97))    

class NumblerConnection:
    """
    Manages connections to your Numbler spreadsheets.  you will need
    to get a Numbler API ID and secret key from numbler before you
    can use this API.
    
    """

    def __init__(self,sheetUID,api_id,secret_key,server=default_server,port=default_port,is_secure=False):
        """
        sheetUID is the identifier of the spreadsheet you wish to use.  it is
        the first part of the URL to your numbler spreadsheet.
        """
        self.api_id = api_id
        self.secret_key = secret_key
        self.sheetUID = sheetUID
        constr = '%s:%d' % (server,port)
        if is_secure:
            self.con = httplib.HTTPSConnection(constr)
        else:
            self.con = httplib.HTTPConnection(constr)


    def createhash(self,method,path,headers):
        """ create the hmac-sha hash

        more readable sample (non optimized):

        contentmd5 = headers.get('content-md5')
        if not contentmd5:
            contentmd5 = ''

        encodestr = 'GET' + '\n' +
        contentmd5 + '\n' +
        'text/xml' + '\n' +
        'Mon, 03 Apr 2006 15:54:13 GMT' + '\n' +
        '/vCskO2bQZfwtRNGR/API/D4'

        base64.encodestring(hmac.new(self.secret_key,encodestr,sha).digest()).strip()
        
        """            
        contentmd5 = headers.get('content-md5')

        encodestr = ''.join([method,'\n',
                 contentmd5 is not None and contentmd5 or '','\n',
                 headers['content-type'],'\n',
                 headers['x-numbler-date'],'\n',
                 path])
        return base64.encodestring(hmac.new(self.secret_key,encodestr,sha).digest()).strip()
                 
    
    def makeRequest(self,method,path,headers = {},data = '',args={}):
        """
        create the HTTP request and send it to the server.
        """
        if path[0] != '/':
            path = '/' + path

        headers['content-type'] = 'text/xml'
        headers['x-numbler-date'] = time.strftime("%a, %d %b %Y %X GMT", time.gmtime())
        headers['Authorization'] = "NUMBLER %s:%s" % (self.api_id,self.createhash(method,path,headers))

        if len(args):
            uri = "%s?%s" % (path,urllib.urlencode(args))
        else:
            uri = path
        
        self.con.request(method,uri,data,headers)
        return self.con.getresponse()
        

    def _cellRequest(self,col,row,method,args={}):
        if type(col) is int:
            col = translatecol(col)
        
        return Response(self.makeRequest(method,'/'.join([self.sheetUID,'API',col+str(row)]),args=args))

    def _cellRangeRequest(self,startcol,startrow,endcol,endrow,method,args={}):
        st = type(startcol)
        if st is int or st is long:
            startcol = translatecol(startcol)
        et = type(endcol)
        if et is int or et is long:
            endcol = translatecol(endcol)

        # use - instead of : for the range deliminator
        rng = ''.join([startcol,str(startrow),'-',endcol,str(endrow)])
        return Response(self.makeRequest(method,'/'.join([self.sheetUID,'API',rng]),args=args))

    def _rowRngRequest(self,startrow,endrow,method,args={}):
        rng = ''.join([str(startrow),'-',str(endrow)])
        return Response(self.makeRequest(method,'/'.join([self.sheetUID,'API',rng]),args=args))    

    def _colRngRequest(self,startcol,endcol,method,args={}):
        st = type(startcol)
        if st is int or st is long:
            startcol = translatecol(startcol)
        et = type(endcol)
        if et is int or et is long:
            endcol = translatecol(endcol)
        rng = ''.join([str(startcol),'-',str(endcol)])
        return Response(self.makeRequest(method,'/'.join([self.sheetUID,'API',rng]),args=args))


    def getCell(self,col,row):
        """
        get a single cell from a numbler spreadsheet.

        Valid values for col: [A - IV] or [1 - 255]
        Valid values for row: [1-65536]
        
        """
        return self._cellRequest(col,row,'GET')

    def getCellRange(self,startcol,startrow,endcol,endrow):
        """
        get a range of cells for a particular region.  Numbler will only
        return cells that are valid (e.g you will get back a sparse result)
        """
        return self._cellRangeRequest(startcol,startrow,endcol,endrow,'GET')

    def getRowRange(self,startrow,endrow):
        """
        get a range of cells based on a row range.  In Numbler you would express the row
        range as 1:4, 10:12, etc.
        """
        return self._rowRngRequest(startrow,endrow,'GET')

    def getColRange(self,startcol,endcol):
        """
        get a range of cells based on a column range.  In Numbler you would express the column
        range as A:E, F:R, etc.
        """
        return self._colRngRequest(startcol,endcol,'GET')

    def deleteCell(self,col,row,getResults = True):
        """
        delete a single cell from a numbler spreadsheet.

        Valid values for col: [A - IV] or [1 - 255]
        Valid values for row: [1-65536]

        """
        args = {}
        if not getResults:
            args['recvResults'] = 0
        
        return self._cellRequest(col,row,'DELETE',args)

    def deleteCellRange(self,startcol,startrow,endcol,endrow,getResults = True):
        """
        delete a range of cells for a particular region.

        by default you will get a list of cells affected by the deletion.  If you set getREsults = False 
        you will get a count of the affected cells.
        """
        args = {}
        if not getResults:
            args['recvResults'] = 0
        
        return self._cellRangeRequest(startcol,startrow,endcol,endrow,'DELETE',args)

    def deleteRowRange(self,startrow,endrow,getResults= True):
        """
        delete a range of cells based on a row range.
        """
        args = {}
        if not getResults:
            args['recvResults'] = 0        
        return self._rowRngRequest(startrow,endrow,'DELETE',args)

    def deleteColRange(self,startcol,endcol,getResults = True):
        """
        delete a range of cells based on a column range
        """
        args = {}
        if not getResults:
            args['recvResults'] = 0        
        return self._colRngRequest(startcol,endcol,'DELETE',args)
        
    def getAllCells(self):
        """
        request all the cells for a spreadsheet.  this could be quite a large
        amount of data!
        """
        return Response(self.makeRequest('GET','/'.join([self.sheetUID,'API'])))        

    def newCellUpdater(self):
        """
        get a request generator object to write cell updates. call sendCells when
        you are done.
        """
        return RequestGenerator(self.sheetUID)

    def sendCells(self,cellgen,getChangedCells=True):
        """
        send cells to Numbler.  if you don't want any changed cells
        set getChangedCells=False.  This means if that if you set a value that causes
        a calculation you will not get the updated cell.
        
        """
        writer = StringIO.StringIO()
        cellgen.generateXML(writer)
        writer.seek(0)

        urlargs = {}
        if not getChangedCells:
            urlargs['recvResults'] = 0
        
        return Response(self.makeRequest('PUT','/'.join([self.sheetUID,'API']),args=urlargs,
                                         data=writer.read()))

        
class Response:
    """
    very lightweight wrapper around the httplib response object.
    """
    
    def __init__(self,response):
        self.contents = response.read()
        self.response = response
        self.error = self.response.status != 200

    def getError(self):
        """
        returns the Numbler error code, the detailed message, and the resource
        """
        if self.error:
            doc = parseString(self.contents)
            # the dom sucks
            return tuple([x.firstChild.data for x in doc.documentElement.childNodes])
        else:
            return None
            



class RequestGenerator:
    """
    generate XML to publish to your spreadsheet.
    """

    def __init__(self,sheetUID):
        self.cells = []
        self.sheetUID = sheetUID

    def addCell(self,col,row,formula):
        if type(col) is int:
            col = translatecol(col)
            
        self.cells.append((col,str(row),str(formula)))

    def generateXML(self,output):

        gen = XMLGenerator(output,"UTF-8")
        gen.startDocument()
        gen.startElement("xml",{});
        gen.startElement("sheet",{'guid':self.sheetUID})
        for cellattrs in [{'col':val[0],'row':val[1],'formula':val[2]} for val in self.cells]:
            gen.startElement("cell",cellattrs)
            gen.endElement("cell")
        gen.endElement("sheet")
        gen.endElement("xml")
        gen.endDocument()
        
        

