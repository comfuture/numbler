# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

import array,traceback,sys,re

from twisted.internet import reactor,defer,threads
from twisted.internet.defer import deferredGenerator,waitForDeferred
from xml.dom.minidom import parseString

from numbler.server.colrow import Col,Row
from numbler.server.sheet import Sheet
from numbler.utils import yieldDef,cellDepFlattener

from numbler.importwarnings import *
from numbler.server.localedb import ParseCtx
from numbler.server.littools import datetimeToSerialDate
from datetime import datetime
import mx.DateTime.ISO


############################################################
## import helper functions
############################################################

r1c1Match = re.compile(r'R(\d+|\[-?[0-9]+\])?C(\d+|\[-?\d+\])?')
sheetRefMatch = re.compile(r'^=([a-zA-Z]|\d)+!$')

def findR1C1(col, row, formula):
    """if no match found, returns None
    else returns CellRef string, start, end"""
    # print "formula:", formula
    match = r1c1Match.search(formula)
    if not match: return

    # print "match:  ", match.group(0)
    rg, cg = match.group(1), match.group(2)
    # print rg, cg
    rAbs, cAbs = True, True
    c, r = Col(col), row
    if rg:
        if rg[0] == '[':
            rAbs = False
            r = row + int(rg[1:-1])
        else:
            r = int(rg)

    if cg:
        if cg[0] == '[':
            cAbs = False
            c = Col(col + int(cg[1:-1]))
        else:
            c = Col(int(cg))

    ref = "%s%s%s%s" % (cAbs and "$" or "", c, rAbs and "$" or "", r)
    return ref, match.start(0), match.end(0)

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc += node.data
    return rc

def r1c1ToA1(col, row, formula,translator):
    """convert R1C1-style references to A1-style references"""
    idx = 0
    out = []
    while 1:
        ret = findR1C1(col, row, formula)
        if ret:
            ref, start, end = ret

            startfrag = formula[:start]
            if sheetRefMatch.search(startfrag):
                target = translator.get(startfrag[1:-1])
                if target:
                    out.append('=%s!' % (target))
                else:
                    out.append(startfrag)
            else:
                out.append(startfrag)
            out.append(ref)
            formula = formula[end:]
            
        else:
            out.append(formula)
            break

    return ''.join(out)
    


class ExcelXMLImporter(object):
    """ Import excel spreadsheets stored in XML """

    numberMapper = {
        'Comma':u',',
        'Currency':u'$',
        'Percent':u'%'
        }
    # maps the contents of ss:Format to our internal rep
    numberFormatMapper = {
        'Short Date':ParseCtx.shortDateFormat,
        'General Date':ParseCtx.dateTimeFormat,
        'Medium Time':ParseCtx.mediumTimeFormat,
        'Long Time':ParseCtx.longTimeFormat,
        'Currency':ParseCtx.currencyFormat,
        '0%':ParseCtx.percentFormat,
        'Scientific':ParseCtx.scientificFormat,
        # hack, like the rest of this fucking module :(
        '"$"#,##0.00':ParseCtx.currencyFormat
        }
    
    fmtMapper = {
        'Bold':(u'font-weight',u'bold'),
        'Color':(u'color',None),
        'Underline':(u'text-decoration',u'underline'),
        'Italic':(u'font-style',u'italic'),
        # we ignore the font family for right now.
        # this was x:Family because excel dumps out the font family
        # in the urn:schemas-microsoft-com:office:excel namespace
        'Family':(None,)
        }
    halignDict = {'Center':u'center','Left':u'left','Right':u'right'}
    

    excelNS = 'urn:schemas-microsoft-com:office:spreadsheet'
    convFactor = 1.333 # conversion multiplier for row heights and col widths
    
    def __init__(self,sourcedata,principal):
        self.sourcedata = sourcedata
        self.dom = None
        self.styles = {}
        self.defaultStyle = None
        self.warnings = {}
        #columns, rows, and cells are reset after every worksheet pass
        self.columns = []
        self.rows = []
        self.cells = []
        self.sheetnames = []
        self.worksheets = {}
        # the current worksheet that is being processed
        self.currentWS = None
        self.targetWS = []
        self.targetSheetH = {}
        self.currentWSIndex = 0
        self.sheetXlate = {}
        self.principal = principal

    def __str__(self):
        return '\n'.join([
            str(self.styles),
            str(self.columns),
            str(self.rows),
            str(self.cells)
            ])

    def addWarning(self,warningType):
        """ add a warning object for later consumption by the UI """
        if not self.warnings.get(warningType.key):
            self.warnings[warningType.key] = warningType

    def warningText(self):
        return map(lambda x: unicode(self.warnings[x].text),
                   self.warnings.keys())

    def _generateDomTree(self):
        """ thread function that is used to parse the source
        data. This runs in a seperate thread because of the potential
        to block the server
        """
        self.dom = parseString(self.sourcedata)
        print 'parse finished'
    def parse(self,d):
        try:
            td = threads.deferToThread(self._generateDomTree)
            # chain simply calls the callback or or errback on d when td fires
            td.chainDeferred(d)
        except Exception,inst:
            print 'ExcelXMLImporter failed to parse:',inst
            d.errback(inst)
            
    def numberOfSheets(self,d):
        try:

            res = self.dom.getElementsByTagNameNS(self.excelNS,"Worksheet")
            for worksheet in res:
                # make sure that there are actually values in the sheet and it is not an
                # empty workbook reference (like sheet1, sheet2, sheet3
                if worksheet.getElementsByTagNameNS(self.excelNS,'Table'):
                    name = worksheet.attributes.getNamedItemNS(self.excelNS,'Name').value
                    self.worksheets[name] = worksheet
                    self.sheetnames.append(name)
            d.callback(len(res))
        except:
            d.errback(0)

    def setTargetSheets(self,targets):
        """ set the currrent worksheet.  Targets is expected to be an array of sheet names"""
        self.targetWS = targets
        if not len(targets):
            return

        # make sure all the worksheets are valid.
        for ws in targets:
            if not self.worksheets.has_key(ws):
                raise "worksheet %s not found" % (ws)

        for ws in self.targetWS:
            self.targetSheetH[ws] = Sheet.getNew(ws,self.principal)
            self.sheetXlate[ws] = str(self.targetSheetH[ws].getHandle())
        self.currentWSIndex = 0
        self.currentWS = self.worksheets[self.targetWS[0]]



    def continueImport(self):
        """ indicate if the UI should continue import. """
        self.currentWSIndex += 1
        if self.currentWSIndex < len(self.targetWS):
            #print 'continueImport',self.currentWSIndex,self.targetWS,self.targetWS[self.currentWSIndex]
            self.currentWS = self.worksheets[self.targetWS[self.currentWSIndex]]
            return True
        else:
            return False
        
    def processStyles(self,d):
        """ process all of the style elements in the XML file

        step 1: grab all of the elements and put in a dictionary
        step 2: iterate through the styles again and process any parent
        directives
        """
        
        try:
            styles = self.dom.getElementsByTagNameNS(self.excelNS,'Style')
            for style in styles:
                id = style.attributes.getNamedItemNS(self.excelNS,'ID').nodeValue 
                if id == 'Default':
                    continue
                result = self.processStyleElement(style)
                if result:
                    self.styles[id] = result

            # colapse the style inheritance.
            for styleID in self.styles.keys():
                style = self.styles[styleID]
                parentID = style.get('parentID')
                if parentID:
                    del style['parentID']
                    sparent = self.styles.get(parentID)
                    if sparent:
                        style.update(sparent)
                    else:
                        print "warning: can't find style parent",parentID

            d.callback(self.styles)
        except Exception, inst:
            print 'processStyles: encountered error import style info',inst
            traceback.print_tb(sys.exc_info()[2])       
            d.errback(inst)

    def processStyleElement(self,style):
        """ process a single style element and convert it into the
        Numbler format.
        """
        ret = {}

        parent = style.attributes.getNamedItemNS(self.excelNS,'Parent')
        if parent:
            if parent.nodeValue != 'Default':
                ret['parentID'] = parent.nodeValue
        
        for childel in style.childNodes:
            res = self.styleMapper.get(childel.localName)
            if res:
                res(self,childel,ret)

            elif childel.nodeName != '#text':
                pass
                #print 'style element not found %s not supported yet'  % (childel.localName)
        return ret

    def fontFormat(self,style,ret):
        for attrNS,attr in style.attributes.keysNS():
            mappedval = self.fmtMapper.get(attr)
            if mappedval:
                if mappedval[0] is None:
                    continue
                if mappedval[1] is None:
                   ret[mappedval[0]] = unicode(style.attributes.getNamedItemNS(attrNS,attr).value)
                else:
                    ret[mappedval[0]] = mappedval[1]
            else:
                self.addWarning(FontWarning)

    def numberFormat(self,style,ret):
        attr = style.parentNode.attributes.getNamedItemNS(self.excelNS,'Name')
        if attr is not None:
            name = attr.value
            ntype = self.numberMapper.get(name)
            if ntype:
                ret[u'__sht'] = ntype
                return

        # try the content of the ss:Format
        attr = style.attributes.getNamedItemNS(self.excelNS,'Format')
        if attr is not None:
            formatstr = attr.value
            mappedtype = self.numberFormatMapper.get(formatstr)
            if mappedtype:
                ret[u'__sht'] = mappedtype
                return
                if mappedtype in ParseCtx.dateIds:
                    # convert the date format to the excel format
                    ISO.ParseAny(formatstr)

        # we don't know how to handle some of the formatting yet
        self.addWarning(StyleWarning)

    def alignFormat(self,style,ret):
        for attrNS,attr in style.attributes.keysNS():
            if attr == 'Horizontal':
                lookupAlign = self.halignDict.get(style.attributes.getNamedItemNS(self.excelNS,attr).value)
                if lookupAlign is not None:
                    ret[u'text-align'] = lookupAlign
                else:
                    self.addWarning(StyleWarning)                                    
            elif attr != 'Vertical':
                self.addWarning(StyleWarning)                

    def interiorFormat(self,style,ret):
        pattern = ''
        color = ''
        for attrns,attr in style.attributes.keysNS():
            if attr == 'Pattern':
                pattern = style.attributes.getNamedItemNS(self.excelNS,attr).value
            elif attr == 'Color':
                color = style.attributes.getNamedItemNS(self.excelNS,attr).value
            else:
                self.addWarning(StyleWarning)
        if pattern == 'Solid' and color:
            ret[u'background-color'] = color
        else:
            self.addWarning(InteriorWarning)

    def processColumns(self,d):
        try:
            cols = self.currentWS.getElementsByTagNameNS(self.excelNS,'Column')
            index = 1
            for col in cols:
                cindex = col.attributes.getNamedItemNS(self.excelNS,'Index')
                if cindex is not None:
                    index = int(cindex.value)

                sID = col.attributes.getNamedItemNS(self.excelNS,'StyleID')
                width = col.attributes.getNamedItemNS(self.excelNS,'Width')
                self.columns.append((index,
                                     sID and sID.value or None,
                                     width and width.value or None))

                index += 1
                
            d.callback(self.columns)
        except Exception,inst:
            print 'failed to process cols;',inst
            d.errback(inst)


    def processRows(self,d):
        try:
            rows = self.currentWS.getElementsByTagNameNS(self.excelNS,'Row')
            index = 1
            for row in rows:
                rindex = row.attributes.getNamedItemNS(self.excelNS,'Index')
                if rindex is not None:
                    index = int(rindex.value)
                
                sID = row.attributes.getNamedItemNS(self.excelNS,'StyleID')
                height = row.attributes.getNamedItemNS(self.excelNS,'Height')
                if sID or height:
                    self.rows.append((index,
                                      sID and sID.value or None,
                                      height and height.value or None))

                self.processRow(row,index)
                index += 1
            #d.callback(self.rows)
        except Exception,inst:
            print 'failed to process rows;',inst
            traceback.print_tb(sys.exc_info()[2])
            #traceback.print_stack()            
            #d.errback(inst)
            raise inst
        

    def processRow(self,row,rIdx):
        cells = row.getElementsByTagNameNS(self.excelNS,"Cell")
        cIdx = 1
        for cell in cells:
            idx = cell.attributes.getNamedItemNS(self.excelNS,"Index")
            if idx:
                cIdx = int(idx.value)

            formula = cell.attributes.getNamedItemNS(self.excelNS,"Formula")
            sID = cell.attributes.getNamedItemNS(self.excelNS,"StyleID")

            nf,dt = '',''
            if formula:
                cellformula = formula.value.encode('utf-8')
                # if it is a formula make sure that it starts with =
                if cellformula and cellformula[0] != '=':
                    temparray = array.array('B','=')
                    temparray.fromstring(cellformula)
                    cellformula = temparray.tostring()
                nf = r1c1ToA1(cIdx, rIdx,cellformula,self.sheetXlate)
            else:
                data = cell.getElementsByTagNameNS(self.excelNS,"Data")
                if len(data):
                    cellType = data[0].attributes.getNamedItemNS(self.excelNS,"Type")
                    if cellType and cellType.value == 'DateTime':
                        if sID:
                            if sID.value not in self.styles:
                                # synthesize a generic date time style
                                self.styles[sID.value] = {u'__sht':ParseCtx.shortDateFormat}
                            else:
                                # make sure that a custom number format is present
                                if u'__sht' not in self.styles[sID.value]:
                                    self.styles[sID.value][u'__sht'] = ParseCtx.shortDateFormat
                if len(data) and len(data[0].childNodes):
                    nodeValue = data[0].childNodes[0].nodeValue
                    if nodeValue:
                        dt = nodeValue.encode('utf-8')
                    else:
                        # this can happen if the value is HTML or something - will fix later
                        self.addWarning(DataImportWarning)
                        dt = ''

            self.cells.append((cIdx,rIdx,sID and sID.value or '',nf or dt))
            cIdx += 1

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
    def generateSheet(self,returndef):
        defwidth = 50
        defheight = 20
        yieldcount = 0
        try:
            # create the sheet.
            newsheet = self.targetSheetH[self.targetWS[self.currentWSIndex]]

            from numbler.server import ssdb,cell

            # bind all the style information to the cells
            for i in range(0,len(self.cells)):
                colid,rowid,styleID,formula = self.cells[i]
                if styleID:
                    targetS = self.styles.get(styleID)
                    # if the value is a date we need to convert it.
                    if targetS is not None and '__sht' in targetS:
                        if targetS['__sht'] in ParseCtx.dateIds:
                            # convert the ISO time to a the serial date rep.
                            # this uses the mx.DateTime.ISO module to parse the string
                            # and then we conver that to a native datetime.
                            try:
                                formula = str(datetimeToSerialDate(datetime(*mx.DateTime.ISO.ParseAny(formula).tuple()[0:6])))
                            except ValueError:
                                # this can happen for a couple of reasons, primarily
                                # if the style was inherited but the value doesn't
                                # look like a date time
                                pass
                    
                    self.cells[i] = (colid,rowid,cell.Cell.toFormatRep(targetS),formula)

            sdb = ssdb.ssdb.getInstance()
            # bulk load all the cell data.  This will run in a seperate thread
            # and this won't get called back until that thread is done
            d = sdb.bulkLoadCells(str(newsheet.getHandle()),self.cells)
            d.addCallbacks(self.runclosure,self.logSqlError)
            yield waitForDeferred(d)            
            # bulk load all of the cell information into the cell cache.  this creates
            # all of the dependencies.
            # TODO: this could block for a while (although everything is in memory)
            cell.Cell.bulkLoadCells(newsheet.getHandle(),self.cells)
            yield waitForDeferred(yieldDef())

            # create and row and column meta data
            for colID,styleID,width in self.columns:
                if width:
                    width = round(float(width) * self.convFactor)
                prop = newsheet.getColProp(colID,width or defwidth)
                # look if any style information exists for rows or columns                
                if styleID and styleID in self.styles:
                    prop.setFormat({u'cache':self.styles[styleID]});
                yieldcount += 1
                newsheet.saveColumnProps(prop)
                if yieldcount % 10 == 0:
                    yield waitForDeferred(yieldDef())

            for rowID,styleID,height in self.rows:
                # convert the excel height into pixels
                if height:
                    height = round(float(height) * self.convFactor)
                prop = newsheet.getRowProp(rowID,height or defheight)
                # look if any style information exists for rows or columns
                if styleID and styleID in self.styles:
                    prop.setFormat({u'cache':self.styles[styleID]});
                yieldcount += 1
                newsheet.saveRowProps(prop)
                if yieldcount % 10 == 0:
                    yield waitForDeferred(yieldDef())

            allcelldeps = []
            allrangedeps = []
                    
            # create cells
            for colID,rowID,styleInfo,formula in self.cells:
                cellH = newsheet.getCellHandle(colID,rowID)
                if formula:
                    if styleInfo:
                        cellH().format = styleInfo
                    cellH().setFormulaFromDb(formula,self.principal.locale)
                    # generate the dependencies for persistance later.
                    celldeps,rangedeps = cellH().bulkGetDeps()
                    if celldeps:
                        allcelldeps.append(celldeps)
                    if rangedeps:
                        allrangedeps.append(rangedeps)

            # bulk load the cell dependencies
            if len(allcelldeps) > 0:
                yield waitForDeferred(sdb.bulkSetDeps(cellDepFlattener(allcelldeps)))
            if len(allrangedeps) > 0:
                yield waitForDeferred(sdb.bulkSetRangeDeps(cellDepFlattener(allrangedeps)))

            self.columns = []
            self.rows = []
            self.cells = []                        
            returndef.callback((str(newsheet.getHandle()),newsheet.getAlias()))

        except Exception,inst:
            print 'Error caught while generating db sheet',inst
            traceback.print_tb(sys.exc_info()[2])
            traceback.print_stack()                        
            returndef.errback(inst)
    
    styleMapper = {
        'NumberFormat':numberFormat,
        'Font':fontFormat,
        'Alignment':alignFormat,
        'Interior':interiorFormat,
        
        }


