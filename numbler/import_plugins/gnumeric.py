# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from xml.sax import make_parser,handler
from twisted.internet import reactor,defer,threads
from twisted.internet.defer import deferredGenerator,waitForDeferred

from numbler.server import engine,sheet,ssdb,cell
from numbler.server.exc import SSError
from gnumeric_conversion import GnumericConverter as gnucon
from numbler.utils import yieldDef,cellDepFlattener

from numbler.server.cell import CellRange
from numbler.server.colrow import Col,Row
import traceback,sys

class abortParse(Exception):
    """ abort the sax parsing."""

class BaseSaxHandler(object):

    def startElement(self,location,qname,attrs):
        pass

    def endElement(self,name):
        if self.name == name:
            #print 'from %s returning %s' % (self.name,self.parent is not None and self.parent.name or 'None')
            return self.parent
        return self
    
    def getchild(self,childname):
        return None

    def characters(self,data,stack):
        pass

    def dump(self):
        pass

class WorkBook(BaseSaxHandler):
    name = 'Workbook'
    children = ['Sheet']

    def __init__(self,parent,principal):
        self.sheets = []
        self.worksheets = []
        self.parent = parent
        self.principal = principal
        # only allow one worksheet right now
        self.allowedchildren = 1
        
    def getchild(self,childname):
        child = WorkSheet(self)
        if len(self.worksheets) < self.allowedchildren:
            self.worksheets.append(child)
            return child
        else:
            raise abortParse()

    def characters(self,data,stack):
        if len(stack) > 1:
            if stack[-2] == 'SheetNameIndex' and stack[-1] == 'SheetName':
                self.sheets.append(data)

    def dump(self):
        print self.sheets
        print self.worksheets

class WorkSheet(BaseSaxHandler):
    name = 'Sheet'
    children = ['Cols','Rows','Cells','Styles']

    def __init__(self,parent):
        self.wsname = ''
        self.parent = parent
        self.rows,self.cols,self.cells,self.styles = None,None,None,None

    def getchild(self,childname):
        if childname == 'Rows':
            self.rows = WsRows(self)
            return self.rows
        elif childname == 'Cols':
            self.cols = WsCols(self)
            return self.cols
        elif childname == 'Cells':
            self.cells = WsCells(self)
            return self.cells
        elif childname == 'Styles':
            self.styles = WsStyles(self)
            return self.styles
        
        
    def characters(self,data,stack):
        if len(stack) > 1:
            if stack[-2] == 'Sheet' and stack[-1] == 'Name':
                self.wsname = data

class WsRows(BaseSaxHandler):
    name = 'Rows'
    children = []
    conv = 4.0/3.0
    
    def __init__(self,parent):
        self.parent = parent
        self.rows = {}

    def startElement(self,name,qname,attrs):
        if name == 'RowInfo':
            rowid = int(attrs[(None,'No')]) + 1
            size = float(attrs[(None,'Unit')]) * self.conv
            self.rows[rowid] = size
    def dump(self):
        print 'row size information'
        for row in self.rows.keys():
            print row,self.rows[row]
        

class WsCols(BaseSaxHandler):
    name = 'Cols'
    children = []
    conv = 4.0/3.0
    
    def __init__(self,parent):
        self.parent = parent
        self.cols = {}

    def startElement(self,name,qname,attrs):
        if name == 'ColInfo':
            colid = int(attrs[(None,'No')]) + 1
            size = float(attrs[(None,'Unit')]) * self.conv
            self.cols[colid] = size

    def dump(self):
        print 'col size information'
        for col in self.cols.keys():
            print col,self.cols[col]
                        
class WsCell:
    def __init__(self,col,row):
        self.col = col
        self.row = row
        self.formula = ''
        self.style = ''

    def key(self):
        return self.col << 16 | self.row

    def setStyles(self,styledict):
        if not self.style:
            self.style = styledict
        else:
            self.style.update(styledict)

    def setStyle(self,attr,value):
        if not self.style:
            self.style = {}
        self.style[attr] = value

    def __str__(self):
        formval = self.formula.encode('utf-8')
        return '%s:%s %s' % (self.col,self.row,formval)


class WsCells(BaseSaxHandler):
    """
    collection of all gnumeric cells.

    Gnumeric decided to compact its cell rep by using expressions
    which refer to previous formulas.  The formula is then loaded relative to
    the original formula stored on the expression.

    """
    
    name = 'Cells'
    children = []

    def __init__(self,parent):
        self.parent = parent
        self.cells = []
        self.current = None
        self.expr = {}
        # parent order: worksheet.Workbook
        self.shtH = sheet.Sheet.getTemp(self.parent.parent.principal).getHandle()
        self.parser = engine.Engine.getInstance().parser
        self.waitingforexpr = None
        self.translatereq = None
        self.content = []
        self.maxcol = 1
        self.maxrow = 1
        
    def startElement(self,name,qname,attrs):        
        if name == 'Cell':
            col = int(attrs[(None,'Col')])+1
            row = int(attrs[(None,'Row')])+1
            self.current = WsCell(col,row)
            expr = attrs.get((None,'ExprID'))
            if expr:
                if expr not in self.expr:
                    self.waitingforexpr = expr
                else:
                    self.translatereq = expr
            valueformat = attrs.get((None,'ValueFormat'))
            if valueformat and valueformat[-1] == '%':
                self.current.setStyle(u'__sht',u'%')
            self.content = []


    def characters(self,content,stack):
        """
        any cells with an exprID must be translated
        """
        if self.current:
            self.content.append(content)

    def endElement(self,name):

        if name == 'Cell' and self.current:
            contentstr = u''.join(self.content).encode('utf-8')
            self.current.formula = contentstr
            self.cells.append(self.current)

            self.maxcol = max(self.maxcol,self.current.col)
            self.maxrow = max(self.maxrow,self.current.row)
            
            if self.waitingforexpr:
                formula = contentstr[1:]
                try:
                    if len(formula):
                        self.expr[self.waitingforexpr] = (self.current.col,self.current.row,
                                                          self.parser.parse(self.shtH,formula))
                    else:
                        pass
                        #print 'empty formula'
                except SSError,e:
                    print 'couldnt parse',formula
                    pass
                    #print 'error converting formula "%s" %s cell:(%s) %s' %\
                    #(formula,e,self.current,self.waitingforexpr)
                    #raise e
                    
                self.waitingforexpr = None
            if self.translatereq:
                expr = self.expr.get(self.translatereq)
                if expr:
                    newformula = expr[2].translate(
                        abs(self.current.col - expr[0]),
                        abs(self.current.row - expr[1]))
                    self.current.formula = "=" + str(newformula)
                else:
                    # raise an error here to user that a translate error has occurred.
                    print 'expression not found!'
                self.translatereq = None
            self.current = None

        return super(WsCells,self).endElement(name)

    def dump(self):
        print 'dumping cells'
        for cell in self.cells:
            print cell


class WsStyles(BaseSaxHandler):
    name = 'Styles'
    children = ['StyleRegion']

    def __init__(self,parent):
        self.parent = parent
        self.styles = {}
        # rows or cols that we are interested in
        self.irows = {}
        self.icols = {}

        # for styles that belong to an entire column or row
        self.gencolstyles = {}
        self.genrowstyles = {}
        self.genstyles = {}

    def getchild(self,childname):
        newchild = WsStyleRegion(self)
        return newchild

    def setchild(self,child):
        self.styles[child.getKey()] = child

    def removechild(self,child):
        if child.getKey() in self.styles:
            del self.styles[child.getKey()]

    def addColTotal(self,col,total,style):
        if col in self.icols:
            self.icols[col][0] += total
            self.icols[col][1].append(style)
        else:
            self.icols[col] = [total,[style]]

    def addRowTotal(self,row,total,style):
        if row in self.irows:
            self.irows[row][0] += total
            self.irows[row][1].append(style)
        else:
            self.irows[row] = [total,[style]]

    def dump(self):
        #for style in self.styles.keys():
        #   print str(self.styles[style])
        pass

    def endElement(self,name):
        if name == self.name:
            self.computeStyles()
            
        return super(WsStyles,self).endElement(name)

    def computeStyles(self):
        """
        compute styles serves a number of purpoess.
        1) it builds column and row styles that gnumeric unfortunately spans
        across lots of seperate rectangles.
        2) computes individual styles for each cell if not associated with a row or column
        """

        self.genInheritance(self.icols,True)
        self.genInheritance(self.irows,False)

        #print '*** inherited col styles ***',self.gencolstyles
        for i in self.gencolstyles.keys():
            temp = WsStyleRegion(None)
            temp.props = self.gencolstyles[i]
            self.gencolstyles[i] = temp.convertProps()

        #print '*** inherited row styles ***',self.genrowstyles
        for i in self.genrowstyles.keys():
            temp = WsStyleRegion(None)
            temp.props = self.genrowstyles[i]
            self.genrowstyles[i] = temp.convertProps()

        for style in self.styles.keys():
            self.styles[style].genAllForRange(self.genstyles)

    def genInheritance(self,plist,cols = True):
        """ generate inheritance from the list"""

        endmarker = (cols == True) and 65536 or 256
        
        intobjs = [(plist[item][1],item) for item in plist.keys() if plist[item][0] == endmarker]
        for accumstyle,stylekey in intobjs:
            if len(accumstyle) == 1:
                # get the props from the single style
                #print 'only one style!',str(accumstyle[0]),accumstyle[0].props
                same = accumstyle[0].nondefault()
            else:
                same = accumstyle[0].cmp(accumstyle[1])
                for i in range(2,len(accumstyle),2):
                    dest = i+1 == len(accumstyle) and (i-1) or i+1
                    same.intersection(accumstyle[i].cmp(accumstyle[dest]))

            #print 'intersection of properties is',same
            styleprops = {}
            for item in same:
                styleprops[item] = accumstyle[0].props[item]
                # clear the item
                for stylereg in accumstyle:
                    # make sure we don't accidently do a set default if also in the row styles
                    stylereg.setdefault(item)
                    if stylereg.isdefault():
                        #print 'removing',str(stylereg),cols
                        self.removechild(stylereg)

            if cols:
                self.gencolstyles[stylekey] = styleprops
            else:
                self.genrowstyles[stylekey] = styleprops
                


class WsStyleRegion(BaseSaxHandler):
    name = 'StyleRegion'
    children = []

    defaults = {
        'alignment':1,
        'fore':'0:0:0',
        'back':'FFFF:FFFF:FFFF',
        'format':'General',
        'bold':0,
        'italic':0,
        'underline':0
       }

    alignConversion  = {2:u'left',4:u'right',8:u'center',32:u'justify'}

    
    def __init__(self,parent):
        self.parent = parent
        self.props = {}
        # set the default properties
        self.props.update(self.defaults)
        self.cr = None
        self.styleVisited = False
        self.fontVisited = False

    def setdefault(self,item):
        self.props[item] = self.defaults[item]

    def isdefault(self):
        return self.props == self.defaults

    def nondefault(self):
        return set([x for x in self.props.keys() if self.props[x] != self.defaults[x]])

    def cmp(self,other):
        return set([x for x in self.props.keys() if self.props[x] == other.props[x]
                   and self.props[x] != self.defaults[x]])

    def getKey(self):
        if not self.cr:
            raise "not initialized yet"
        else:
            return self.cr.getKey()
        
    def startElement(self,name,qname,attrs):
        if name == self.name:
            self.startcol = int(attrs[(None,'startCol')])+1
            self.startrow = int(attrs[(None,'startRow')])+1
            self.endcol = int(attrs[(None,'endCol')])+1
            self.endrow = int(attrs[(None,'endRow')])+1
            self.cr = CellRange(Col(self.startcol),self.startrow,Col(self.endcol),self.endrow)
        elif name == 'Style' and not self.styleVisited:
            try:
                self.props['alignment'] = int(attrs[(None,'HAlign')])
                self.props['fore'] = attrs[(None,'Fore')]
                self.props['back'] = attrs[(None,'Back')]
                self.props['format'] = attrs[(None,'Format')]
            except Exception,e:
                print 'style stuff: Exception occured',e,self.startcol,self.startrow,self.endcol,self.endrow
                raise e
            self.styleVisited = True
        elif name == 'Font' and not self.fontVisited:
            self.props['bold'] = int(attrs[(None,'Bold')])
            self.props['italic'] = int(attrs[(None,'Italic')])
            self.props['underline'] = int(attrs[(None,'Underline')])
            self.fontVisited = True

    def endElement(self,name):
        if name == self.name:
            if self.props != self.defaults and not \
            (self.startcol == 1 and self.startrow == 1 \
             and self.endcol== 256 and self.endrow == 65536):
                self.parent.setchild(self)

                ## NOTE: this could doesn't do the right thing
                # for overlapping style regions.  see ticket #121
                
                for i in range(self.startcol,self.endcol+1):
                    #print 'processing col',i,self.endrow-self.startrow
                    self.parent.addColTotal(i,self.endrow-self.startrow+1,self)
                for i in range(self.startrow,self.endrow+1):
                    #print 'processing row',i,self.endcol-self.startcol
                    self.parent.addRowTotal(i,self.endcol-self.startcol+1,self)
            else:
                #print 'removing unnecessary style'
                pass
            
        return super(WsStyleRegion,self).endElement(name)
    
    def __str__(self):
        return str(self.cr)

    def genAllForRange(self,styledict):
        props = self.convertProps()
        if not len(props):
            return
        assert self.startcol != 0
        assert self.startcol != 0
        for i in range(self.startcol,self.endcol+1):
            for j in range(self.startrow,self.endrow+1):
                styledict[i << 16 | j] = props
        
    def convertProps(self):
        """ convert gnumeric properties to the numbler format """
        nondef = self.nondefault()
        ret = {}
        for prop in nondef:
            val = self.props[prop]
            if prop == 'italic' and val == 1:
                ret[u'font-style'] = u'italic'
            elif prop == 'underline' and val == 1:
                ret[u'text-decoration'] = u'underline'
            elif prop == 'bold' and val == 1:
                ret[u'font-weight'] = u'bold'
            elif prop == 'back':
                ret[u'background-color'] = u''.join(['#',u''.join([len(x) <2 and (x[0]+x[0]) or x[0:2]
                                                                   for x in val.split(':')])])
            elif prop == 'fore':
                ret[u'color'] = u''.join(['#',u''.join([len(x) <2 and (x[0]+x[0]) or x[0:2]
                                                                   for x in val.split(':')])])
            elif prop == 'alignment':
                if val in self.alignConversion:
                    ret[u'text-align'] = self.alignConversion[val]
            elif prop == 'format':
                if val[-1] == '%':
                    ret[u'__sht'] = u'%'
        return ret

class GnumericHandler(handler.ContentHandler):

    def __init__(self,principal):
        self.stack = []
        self.wb = WorkBook(None,principal)
        self.stack = [self.wb]
        self.current = self.wb

    def startParse(self,data):
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces, 1)        
        parser.setContentHandler(self)
        try:
            parser.parse(data)
        except abortParse,e:
            print 'parsing aborted (probably multiple sheets)'
        

    def startDocument(self):
        pass

    def endDocument(self):
        print 'done with the doc'

    def startElementNS(self,name,qname,attrs):
        uri,location = name
        #print location
        if location in self.current.children:
            
            self.current = self.current.getchild(location)

        self.current.startElement(location,qname,attrs)        
        self.stack.append(location)

    def endElementNS(self,name,qname):
        self.current = self.current.endElement(name[1])
        self.stack.pop()

    def characters(self,content):
        self.current.characters(content,self.stack)


class GnumericImporter(object):

    def __init__(self,sourcedata,sheetname,principal):
        self.sourcedata = sourcedata
        self.sheetname = sheetname
        self.xmlparsefailed = True
        self.principal = principal

    def gnumericConversion(self):

        d = defer.Deferred()
        d.addCallbacks(self.startParse,self.conversionError)
        converter = gnucon(self.sourcedata,d)
        converter.startprocess()
        return d

    @deferredGenerator
    def startParse(self,data):
        print 'started parsing'
        yield waitForDeferred(threads.deferToThread(self.internalStartParse,data))

    def internalStartParse(self,data):
        self.ghandler = GnumericHandler(self.principal)
        self.ghandler.startParse(data)
        self.xmlparsefailed = False

    def conversionError(arg):
        print arg
        self.xmlparsefailed = False
        
    def continueImport(self):
        return False


    def runclosure(self,arg):
        """
        run the closure returned by the ssdb layer. this must
        run in the main thread because we don't have locks around
        the various MRUdicts
        """
        arg()

    def logSqlError(self,arg):
        print 'bulkCellUpdate: SQL error',arg

    @deferredGenerator
    def generateSheet(self,onfinish):
        #d = threads.deferToThread(self.gnumericConversion)

        try:
            d = self.gnumericConversion()
            yield waitForDeferred(d)
            print 'looks like we are done with parsing'
            if self.xmlparsefailed:
                print 'cannot generated sheet'
                onfinish.errback(None)
                return

            # only do the first worksheet right now
            ws = self.ghandler.wb.worksheets[0]
            gs = ws.styles.genstyles

            # bind styles to the cells
            print 'number of cells',len(ws.cells.cells)
            for cellobj in ws.cells.cells:
                if cellobj.key() in gs:
                    cellobj.setStyles(gs[cellobj.key()])
                    del gs[cellobj.key()]
            yield waitForDeferred(yieldDef())

            print 'left over styles',len(gs.keys())
            print 'maxcol,maxrow:',ws.cells.maxcol,ws.cells.maxrow
            # create extra cells that only have style information

            yieldcount = 0
            for stylekey in gs.keys():
                yieldcount += 1
                col,row = (stylekey >> 16),(stylekey & 0xFFFF)
                if col < 1 or row < 1:
                    continue
                if col <= ws.cells.maxcol and row <= ws.cells.maxrow:
                    newcell = WsCell(col,row)
                    newcell.style = gs[stylekey]
                    ws.cells.cells.append(newcell)
                    if yieldcount % 100 == 0:
                        yield waitForDeferred(yieldDef())
                        
            yield waitForDeferred(yieldDef())            
            print 'generating cell tuples'
            
            celltuples = [(cellObj.col,cellObj.row,
                           cell.Cell.toFormatRep(cellObj.style),
                           cellObj.formula) for cellObj in ws.cells.cells]
            yield waitForDeferred(yieldDef())            


            sheetH = sheet.Sheet.getNew(self.sheetname,self.principal)
            sdb = ssdb.ssdb.getInstance()
            # bulk load all the cell data.  This will run in a seperate thread
            # and this won't get called back until that thread is done
            d = sdb.bulkLoadCells(str(sheetH.getHandle()),celltuples)
            d.addCallbacks(self.runclosure,self.logSqlError)
            yield waitForDeferred(d)
            print 'bulking loading cells'
            cell.Cell.bulkLoadCells(sheetH.getHandle(),celltuples)
            print 'done bulk loading'
            yield waitForDeferred(yieldDef())

            allcelldeps = []
            allrangedeps = []

            # create cells
            for colID,rowID,styleID,formula in celltuples:
                yieldcount += 1
                cellH = sheetH.getCellHandle(colID,rowID)
                if formula:
                    cellH().setFormulaFromDb(formula,self.principal.locale)
                    # generate the dependencies for persistance later.
                    celldeps,rangedeps = cellH().bulkGetDeps()
                    if celldeps:
                        allcelldeps.append(celldeps)
                    if rangedeps:
                        allrangedeps.append(rangedeps)
                if yieldcount % 10 == 0:
                    yield waitForDeferred(yieldDef())
                    
            print 'done generating cells, generating deps'
            # bulk load the cell dependencies
            if len(allcelldeps) > 0:
                yield waitForDeferred(sdb.bulkSetDeps(cellDepFlattener(allcelldeps)))
            if len(allrangedeps) > 0:
                yield waitForDeferred(sdb.bulkSetRangeDeps(cellDepFlattener(allrangedeps)))
            print 'done setting deps'

            defwidth = 50
            defheight = 20
            # save the column widths
            cols = ws.cols.cols

            print '%d cols to save' % (len(cols.keys()))
            ckeys = cols.keys()
            ckeys.sort()
            for col in ckeys:
                yieldcount += 1                
                if col > ws.cells.maxcol:
                    break
                size = cols[col]
                prop = sheetH.getColProp(col,size)
                if col in ws.styles.gencolstyles:
                    prop.setFormat({u'cache':ws.styles.gencolstyles[col]})
                    del ws.styles.gencolstyles[col]
                sheetH.saveColumnProps(prop)
                if yieldcount % 10 == 0:
                    yield waitForDeferred(yieldDef())

            #process any styles that are left over
            cskeys = ws.styles.gencolstyles.keys()
            cskeys.sort()
            for colid in cskeys:
                yieldcount += 1                
                if colid > ws.cells.maxcol:
                    break
                prop = sheetH.getColProp(colid,defwidth)
                prop.setFormat({u'cache':ws.styles.gencolstyles[colid]})
                sheetH.saveColumnProps(prop)
                if yieldcount % 10 == 0:
                    yield waitForDeferred(yieldDef())                

            # save the rows widths
            rows = ws.rows.rows
            rkeys = rows.keys()
            rkeys.sort()
            for row in rkeys:
                yieldcount += 1                
                if row > ws.cells.maxrow:
                    break
                size = rows[row]
                prop = sheetH.getRowProp(row,size)
                if row in ws.styles.genrowstyles:
                    prop.setFormat({u'cache':ws.styles.genrowstyles[row]})
                    del ws.styles.genrowstyles[row]
                sheetH.saveRowProps(prop)
                if yieldcount % 10 == 0:
                    yield waitForDeferred(yieldDef())                                


            rstylekeys = ws.styles.genrowstyles.keys()
            rstylekeys.sort()
            for rowid in rstylekeys:
                yieldcount += 1                                
                if rowid > ws.cells.maxrow:
                    break
                prop = sheetH.getRowProp(rowid,defheight)
                prop.setFormat({u'cache':ws.styles.genrowstyles[rowid]})
                sheetH.saveRowProps(prop)
                if yieldcount % 10 == 0:
                    yield waitForDeferred(yieldDef())                

            onfinish.callback((str(sheetH.getHandle()),sheetH.getAlias()))
        except Exception,inst:
            print 'Error caught while generating db sheet',inst
            traceback.print_tb(sys.exc_info()[2])
            traceback.print_stack()                        
            onfinish.errback(inst)            



def tester():

    eng = engine.Engine.getInstance()

    def startParse(data):
        print 'starting parser'
        ghandler = GnumericHandler()
        ghandler.startParse(data)

        wb = ghandler.wb
        print 'sheets:',wb.sheets
        for ws in wb.worksheets:
            print ws.wsname
            #if ws.rows:
            #    ws.rows.dump()
            #if ws.cols:
            #    ws.cols.dump()
            #if ws.cells:
            #    ws.cells.dump()
            if ws.styles:
                ws.styles.dump()
        reactor.stop()

    def bail(arg):
        print "failed to general XML from XLS. can't parse"
        reactor.stop()

    from twisted.internet import reactor    
    import sys
    
    if len(sys.argv) < 2:
        print 'file name required'
        return

    d = defer.Deferred()
    d.addCallbacks(startParse,bail)
    converter = gnucon(open(sys.argv[1],'rb').read(),d)
    converter.startprocess()
    reactor.run()


if __name__ == '__main__': tester()
    
    
