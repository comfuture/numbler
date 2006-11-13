# (C) Numbler Llc 2006
# See License For Details.

#
# queries and other backend goodness
#

from sslib import mrudict
import db
from sslib.utils import guidbin,alphaguid20
from account import Principal
from exc import *
import sha
from colrow import Col,Row

class ssInit(db.Db):

    db = 'ssdb'

    def __init__(self):
        self.db = 'mysql'
        db.Db.__init__(self, 'ssdb', 'ssdb')

    # Creates ssdb database, user
    def buildDB(self):
        self.cursor = self.dbc.cursor()

        self.sql("""create database ssdb""")

#        self.sql("""insert into db (Host, Db, User, Select_priv, Insert_priv, Update_priv, Delete_priv, Create_priv, Drop_priv, Grant_priv, References_priv, Index_priv, Alter_priv) values ('localhost', 'ssdb', 'ssdb', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y')""")

    def tweakUser(self):
        self.sql("""delete from user where user='ssdb'""")
        self.sql("""insert into user (host, user) values ('localhost', 'ssdb')""")
        self.sql("""update user set password=password('ssdb'), select_priv='Y', insert_priv='Y', update_priv='Y', delete_priv='Y', create_priv='Y', drop_priv='Y', reload_priv='Y', shutdown_priv='Y', process_priv='Y', file_priv='Y', grant_priv='Y', references_priv='Y', index_priv='Y', alter_priv='Y', show_db_priv='Y', super_priv='Y', create_tmp_table_priv='Y', lock_tables_priv='Y', execute_priv='Y', repl_slave_priv='Y' where user='ssdb'""")
        self.sql('flush privileges')


 # if you don't want to do init just do this from the mysql console:
 #
 # GRANT all privileges on ssdb.* to 'ssdb'@'localhost' IDENTIFIED BY 'ssdb' WITH GRANT option;


def scrToKey(sheetId, col, row):
    return long(sheetId) << 24 | (int(col - 1) << 16) | int(row - 1)

class ssdb(db.Db):

    db = 'ssdb'

    tables = {
        'sheet': [['sheetId', 'integer unsigned not null primary key auto_increment'],
                  ['sheetUid', 'char(16) UNIQUE', '8'],
                  ['colWidth', 'smallint unsigned'],
                  ['rowHeight', 'smallint unsigned'],
                  ['format', 'text'],
                  ['type','smallint unsigned not NULL']
                  ],
        'account': [['id_acc','integer unsigned not null primary key auto_increment'],
                    ['dt_crt','DATETIME not null'],
                    ['dt_closed','DATETIME null'],                    
                    ['sz_user','varchar(255) not null UNIQUE','idx'],
                    ['sz_displayname','varchar(255) not null'],
                    ['pass','binary(20) not null'],
                    ['salt','binary(20) not null'],
                    # api key used for API requests
                    ['api_id','char(20) NULL','idx'],
                    # secret key for use with HMAC
                    ['api_key','binary(20) NULL','idx'],                    
                    ['acc_type','smallint unsigned'],
                    ['state','smallint unsigned'],
                    ['statetoken','binary(20) null','idx'],
                    ['statetoken_dtcrt','DATETIME null'],
                    ['sz_pendinguser','varchar(255) NULL'],
                    ['sz_locale','varchar(20) not NULL'],
                    ['sz_tz','varchar(40) not NULL']
        ],
        'acc_sheet_map': [['id_acc','integer unsigned not null','idx'],
                          ['sheetId','integer unsigned not null','idx'],
                          ['owner','tinyint(1)']
                          ],
        'acc_invite_pending': [['id_inviter','integer unsigned not null','idx'],
                               ['sheetId','integer unsigned not null'],
                               ['sz_email','varchar(255) not null','idx']
                               ],
        'sheetalias': [['sheetId', 'integer unsigned not null primary key UNIQUE', 'idx'],
                       ['alias', 'tinytext']
                       ],

        'cell': [['cellId', 'integer unsigned not null primary key auto_increment'],
                 ['sheetId', 'integer unsigned not null', 'idx'],
                 ['col', 'tinyint unsigned not null',],
                 ['row', 'smallint unsigned not null',],
                 # ['rev', 'smallint', 'idx']   # revision
                 ['formula', 'mediumtext'],
                 ['format', 'text']],

        'dep': [['observed', 'integer unsigned not null', 'idx'],
                ['observer', 'integer unsigned not null', 'idx']],

        'range': [['rangeId', 'integer unsigned not null primary key auto_increment'],
                  ['observer', 'integer unsigned not null'],            # cell observing this range
                  ['sheetId', 'integer unsigned not null', 'idx'],      # id of sheet containing range
                  ['ulCol', 'tinyint unsigned not null'],               # col: upper left
                  ['ulRow', 'smallint unsigned not null'],              # row: upper left
                  ['lrCol', 'tinyint unsigned not null'],               # col: lower right
                  ['lrRow', 'smallint unsigned not null']],             # row: lower right

        'col': [['sheetId', 'integer unsigned not null', 'idx'],
                ['colid', 'smallint','idx'],
                ['width', 'smallint'],
                ['format', 'text']],

        
        'row': [['sheetId', 'integer unsigned not null', 'idx'],
                ['rowid', 'smallint','idx'],
                ['height', 'smallint'],
                ['format', 'text']],
        
        'remote_txn' : [['txnId', 'integer unsigned not null primary key auto_increment','idx'],
                        ['dt_expire','DATETIME not null'],
                        ['sheetId','integer unsigned not null'],
                        ['colid','integer unsigned not null'],
                        ['rowid','integer unsigned not null']
                       ],
        'txn_ids' : [['id_request','integer unsigned not null primary key auto_increment','idx'],
                     ['req_start','integer unsigned not null'],
                     ['req_end','integer unsigned not null']
                     ]
        }

    def __init__(self, log=None):
        db.Db.__init__(self, 'ssdb', 'ssdb', log)
        # db.Db.__init__(self, 'ssdb', '2paq', log)

        self.sheetIdCache = mrudict.MRUDict(512)   # sheetUid to sheetId
        self.cellIdCache = mrudict.MRUDict(16384)  # for cell key to cellId lookups   
        self.APIauthCache = mrudict.MRUDict(1024)  # for non session based lookups (web services)
        self.authCache = mrudict.MRUDict(1024)     # for username /pass lookups 
        self.batchDbCtx = None

    indexes = [
        "create index cell_colrow on cell (col, row)",
        "create UNIQUE index dep_unique_idx on dep (observed,observer)",
        "create UNIQUE index cell_unique_idx on cell (sheetId,col,row)",
        "create unique index col_unique_idx on col (sheetId,colid)",
        "create unique index row_unique_idx on row (sheetId,rowid)",
        "create unique index map_unique_idx on acc_sheet_map (id_acc,sheetId,owner)",
        "create unique index invite_unique_idx on acc_invite_pending (sheetId,sz_email)",
        "create unique index remote_txn_index on remote_txn (sheetId,colid,rowid)",
       ]

    def createIndices(self):
        db.Db.createIndices(self)
        for idx in self.indexes:
            self.sql(idx)

    def createDefaultEntries(self):
        self.sql("""insert into account (dt_crt,sz_user,sz_displayname,pass,acc_type,state) values (UTC_TIMESTAMP(),'__defuser','__defuser',SHA('1234SDF#@$@#42323!!(@@(*'),1,0)""")

    ##
    ## Sheet mgmt
    ##
    def addSheet(self, sheetUid,private=1):
        """Add a new sheet.  Returns id"""
        ret = self.isql("insert into sheet(sheetUid,type) values (%s,%s)",[sheetUid,private])
        return ret,private

    def modifySheetType(self,sheetUid,stype):
        """ modify the type of sheet (public,private, or whatever) """
        id,oldtype,owner = self.getSheetId(sheetUid)
        self.sql('update sheet set type = %s where sheetUid = %s',[stype,sheetUid])
        self.sheetIdCache[sheetUid] = id,stype,owner
        

    def _getSheetId(self, sheetUid):
        """returns sheetId.  if does not exist, returns None"""
        if sheetUid in self.sheetIdCache:
            id,stype,owner = self.sheetIdCache[sheetUid]
            # print "_getSheetId cached", sheetUid, id
            # this gets really annoying as this is called over and over so I removed it
            #self.log.info("retrieved id", id, "for", sheetUid, "from sheetIdCache", 
            #              len(self.sheetIdCache), "/", self.sheetIdCache.capacity)
            return id,stype,owner

        val = self.rsql('select s.sheetid,s.type,m.id_acc from sheet s '\
                        'INNER JOIN acc_sheet_map m on m.sheetId = s.sheetId '\
                        'where sheetUid = %s',[sheetUid])
        if val:
            ret = val[0]
            self.sheetIdCache[sheetUid] = ret[0],ret[1],ret[2]
            return ret
        else:
            return None,None,None

    def getSheetUid(self,sheetId):
        return self.usql("select sheetUid from sheet where sheetid = %s",[sheetId])

    def sheetExists(self,sheetUid):
        """ returns boolean value if sheet exists in the Db"""
        if self._getSheetId(sheetUid) == (None,None,None):
            return False
        return True

    def getSheetId(self, sheetUid,id_acc = None):
        """returns sheetId.  if does not exist, creates"""
        # contains a tuple of id, sheettype (stype), and the owner account i
        vals = self._getSheetId(sheetUid)
        if not vals[0]: # id
            id,stype = self.addSheet(sheetUid)
            self.sheetIdCache[sheetUid] = id,stype,id_acc
            vals = id,stype,id_acc
        return vals

    def getSheetAlias(self, sheetUid):
        id,stype,owner = self.getSheetId(sheetUid)
        return self.usql("select alias from sheetalias where sheetid = '%s'" % id),stype,id,owner

    def getSheetAliases(self, sheetUid):
        """get the alias of one or more sheets.  SheetUid should be in tuple format."""
        if type(sheetUid) == tuple and len(sheetUid) == 1:
            val = "('%s')" % sheetUid[0]
        else:
            val = str(sheetUid)
        return self.dbpool.runQuery("select alias, sheetUid from sheet, sheetalias where sheetUid in %s and sheet.sheetid = sheetalias.sheetid" % val)
        
    def setSheetAlias(self, sheetUid, alias,principal):
        id,stype,owner = self.getSheetId(sheetUid,principal.acc_id)
        self.insertOrSet("sheetalias", {"sheetid": id},
                         {"alias": self.escape(alias)})
        self.insertOrSet("acc_sheet_map",{"id_acc":principal.acc_id},{"owner":1,"sheetId":id})
        principal.updateOwnedSheets(id)
        return id

    def updateSheetAlias(self,sheetId,alias,principal):
        if sheetId in principal.ownedsheets:
            self.insertOrSet("sheetalias",{"sheetid":sheetId},{"alias":alias})
        else:
            raise "User not authorized"
        
        
    # TEST CODE ONLY: don't use this in production
    # there can be many sheets with the same alias
    def getSheetIdByAlias(self, alias):
       """look for sheet with given alias.  FIXME: this changes when
       we add account support"""
       return self.usql("select sheetId from sheetalias where alias = '%s'" % alias)

    ##
    ## cell mgmt
    ## 

    # NOTE: col and row values in database are n - 1, so that the
    # sheet's 1-256 and 1-65536 values will fit into 8 and 16 bits

    def _getCellIds(self, sheetId):
        """returns all cellIds for given sheet"""
        return [x[0] for x in self.rsql("select cellid + 1 from cell where sheetid = %d" % (sheetId))]

#    def scrToKey(cls, sheetId, col, row):
#        return long(sheetId) << 24 | (int(col - 1) << 16) | int(row - 1)
#    scrToKey = classmethod(scrToKey)

    def _getCellId(self, sheetUid, col, row):
        sheetId = self.getSheetId(sheetUid)[0]

        key = scrToKey(sheetId, col, row)
        if key in self.cellIdCache:
            id = self.cellIdCache[key]
            #if self.log is not None:
            #    self.log.info("retrieved id", id, "for", sheetUid, col, row, "from cellIdCache", 
            #                  len(self.cellIdCache), "/", self.cellIdCache.capacity)
            return id
        id = self.usql("select cellid from cell where sheetid = %d and col = %d - 1 and row = %d - 1" % (sheetId, col, row))
        if id: self.cellIdCache[key] = id
        return id

    def safeGetCellId(self,sheetUid,col,row):
        id = self._getCellId(sheetUid,col,row)
        if id is None:
            sheetId = self.getSheetId(sheetUid)[0]
            id = self.insert("cell", "cellid",
                                         {"sheetId": sheetId, "col": int(col) - 1, "row": int(row) - 1},
                                         {"formula": "", "format": ""})
            key = scrToKey(sheetId, col, row)
            self.cellIdCache[key] = id
        return id

    def getCell(self, sheetUid, col, row):
        cellId = self._getCellId(sheetUid, col, row)
        if not cellId: return None
        return self.osql("select formula, format from cell where cellid = %d" % (cellId))

    def getCells(self, sheetUid):
        """returns all cells in sheet"""
        sheetId = self.getSheetId(sheetUid)[0]
        # FIXME: bulk-load cellId cache for later lookups?
        return self.rsql("select col + 1, row + 1, formula, format from cell where sheetid = %d "
                         "AND (formula <> '' OR format <> '')" % (sheetId))


    def bulkLoadCells(self,sheetUid,cells):
        """ run the bulk loader through the twisted connection pool"""
        return self.dbpool.runInteraction(self._bulkLoadRunner,sheetUid,cells)

    def _bulkLoadRunner(self,txn,sheetUid,cells):
        """ prep the database for a large number cells by prefetching the cell IDs
        cells is assumed to be a list of cells with at the first arg being
        the column and the second the row.
        """
        
        sheetId = self.getSheetId(sheetUid)[0]
        txn.execute('insert into cell (sheetId,col,row,formula,format) values %s '\
                    'ON DUPLICATE KEY update formula=VALUES(formula),format=VALUES(format)' % \
                 ','.join(["(%s,%s,%s,'%s','%s')"% (str(sheetId),str(cell[0]-1),str(cell[1]-1),self.escape(str(cell[3])),
                           self.escape(str(cell[2]))) for cell in cells]))
        txn.execute('select cellid,col,row from cell where sheetId = %d' % sheetId)
        values = txn.fetchall()

        def popCellIdCache():
            for id,col,row in values:
                self.cellIdCache[scrToKey(sheetId,col+1,row+1)] = id
        return popCellIdCache

    
    def setCell(self, formula, format, sheetUid, col, row):
        sheetId = self.getSheetId(sheetUid)[0]
        assert formula is not None
        assert format is not None

        if not self.batchDbCtx:
            cellId = self.insertOrSet("cell", {"sheetId": sheetId, "col": int(col) - 1, "row": int(row) - 1},
                         {"formula": self.escape(formula), "format": self.escape(format)})
            if cellId:
                key = scrToKey(sheetId,col,row)
                if key not in self.cellIdCache:
                    self.cellIdCache[key] = cellId
        else:
            # update or insert
            self.batchDbCtx.cellupdates.append(("(%s,%s,%s,'%s','%s')" % \
                                                   (str(sheetId),str(int(col)-1),str(int(row) -1),
                                                    self.escape(formula),self.escape(format))))

    def deleteCell(self, sheetUid, col, row):
        # ensure cellid cleared out of dep, range
        sheetId= self.getSheetId(sheetUid)[0]
        key = scrToKey(sheetId, col, row)
        if key in self.cellIdCache:
            del self.cellIdCache[key]

        if not self.batchDbCtx:
            self.sql("delete from cell where sheetId = '%d' and col = %d - 1 and row = %d - 1" % (sheetId, col, row))
        else:
            self.batchDbCtx.celldeletes.append("(sheetId = %d  and col = %d -1 and row = %d -1)" \
                                                   % (sheetId,col,row))

    def deleteSheet(self, sheetUid):
        sheetId = self._getSheetId(sheetUid)[0]

        if not sheetId: return
        
        # clear cache
        del self.sheetIdCache[sheetUid]

        # blow out cell dependencies
        cellIds = self._getCellIds(sheetId)

        for cellId in cellIds:
            if cellId in self.cellIdCache:
                del self.cellIdCache[cellId]

        # delete in a seperate thread.
        d = self.dbpool.runInteraction(self.deleteSheetFromDb,cellIds,sheetId)
        d.addErrback(self.dumpErrs)
        return d

    def dumpErrs(self,arg):
        print 'error occured deleting sheet',arg
        return arg
    
    def deleteSheetFromDb(self,txn,cellIds,sheetId):

        try:
            txn.executemany("delete from dep where observer = %s", cellIds)
            txn.executemany("delete from dep where observed = %s", cellIds)
            txn.executemany("delete from range where observer = %s", cellIds)
            txn.execute("delete from cell where sheetId = %s",[sheetId])
            txn.execute("delete from col where sheetId = %s",[sheetId])
            txn.execute("delete from row where sheetId = %s",[sheetId])
            txn.execute("delete from sheet where sheetId = %s",[sheetId])
            txn.execute("delete from sheetalias where sheetId = %s",[sheetId])
            txn.execute("delete from acc_sheet_map where sheetId = %s",[sheetId])
            txn.execute("delete from acc_invite_pending where sheetId = %s",[sheetId])
        except Exception,e:
            print 'error occurred deleting db',e
            raise e

    # FIXME: deprecated
    def deleteCells(self, sheetUid, cellRange):
        """delete a rectangular area of cells identified by the left top and right bottom coordinates
        """
        # sanity check on the passed in values
        dbvals = cellRange.get()
        self.sql("""
        delete cell from cell,sheet
        where sheet.sheetUid = '%s' and sheet.sheetId = cell.sheetId
        and col between %d and %d and row between %d and %d""" %
                 (sheetUid,dbvals[0],dbvals[2],dbvals[1],dbvals[3]))
    ##
    ## Dependency mgmt
    ##
    def setDep(self, observed, observer):
        """
        observed: a tuple: (sheetUid, col, row)
        observer: a tuple: (sheetUid, col, row)
        """

        if not self.batchDbCtx:
            observedCellId, observerCellId = self._getCellId(*observed), self._getCellId(*observer)
            if not observedCellId:
                sheetId = self.getSheetId(observed[0])[0]
                observedCellId = self.insert("cell", "cellid",
                                             {"sheetId": sheetId, "col": int(observed[1]) - 1, "row": int(observed[2]) - 1},
                                             {"formula": "", "format": ""})
                self.cellIdCache[scrToKey(sheetId, observed[1], observed[2])] = observedCellId

            self.insertOrSet("dep", {"observed": observedCellId, "observer": observerCellId}, {})
        else:
            # save off the information for later so we can do a big db insert.
            self.batchDbCtx.depinserts.append((self.getSheetId(observed[0])[0],
                                               self.getSheetId(observer[0])[0],
                                               observed,observer))

    def bulkSetDeps(self,deps):
        """ run the bulk depdenency import through the twisted connection pool """
        return self.dbpool.runInteraction(self._bulkSetDepRunner,deps)

    def _bulkSetDepRunner(self,txn,deps):
        """
        bulk set a number of dependencies.  This will fall over
        if you pass in an empty list!!  we don't check that here because you could
        be using a generator
        """
        txn.execute('insert into dep (observed,observer) values %s' % \
                 ','.join(['(%s,%s)' % (dep[0],dep[1]) for dep in deps]))

    def deleteDep(self, observed, observer):
        """
        observed: a tuple: (sheetUid, col, row)
        observer: a tuple: (sheetUid, col, row)
        """
        observedCellId, observerCellId = self.safeGetCellId(*observed), self.safeGetCellId(*observer)

        #print 'deleteDep called for',observed,observer
        #print 'ids:',observedCellId,observerCellId

        if not self.batchDbCtx:
            self.sql("delete from dep where observed = %d and observer = %d" % (observedCellId, observerCellId))
        else:
            self.batchDbCtx.depdeletions.append("(observed = %d and observer = %d)" % (observedCellId, observerCellId))

    def clearDeps(self, observer):
        """
        observer: a tuple: (observerSheetUid, observerCol, observerRow)
        """
        cellId = self._getCellId(*observer)
        if not cellId: return
        self.sql("delete from dep where observer = %d" % cellId)

    def getDependsOnMe(self, observed):
        """
        return all the observers for this cell
        observed: a tuple: (observedSheetUid, observedCol, observedRow)
        """
        cellId = self._getCellId(*observed)
        if cellId is None: return

        return self.rsql("select cell.col + 1, cell.row + 1, sheet.sheetUid from sheet, cell, dep " \
                         "where sheet.sheetId = cell.sheetId and " \
                         "cell.cellId = dep.observer and " \
                         "dep.observed = %s" % cellId)

    def getAllDeps(self, sheetUid):
        """
        return all the observers for all cells in this sheet
        returns [[col, row, depCol, depRow, depSheetUid)] ...]
        """
        return self.rsql("select cell.col + 1, cell.row + 1, depCell.col + 1, depCell.row + 1, depSheet.sheetUid from " \
                         "sheet, sheet as depSheet, cell, cell as depCell, dep " \
                         "where sheet.sheetId = cell.sheetId and " \
                         "cell.cellId = dep.observed and " \
                         "depCell.cellId = dep.observer and " \
                         "depSheet.sheetId = depCell.sheetId and " \
                         "sheet.sheetUid = '%s'" % sheetUid)

    ##
    ## Range mgmt
    ##
    def setRangeDep(self, sheetUid, ulCol, ulRow, lrCol, lrRow, observer):
        """
        sheetUid: sheet containing range
        ulCol: upper left Column
        ulRow: upper left Row
        lrCol: lower right Column
        lrRow: lower right Row
        observer: a tuple: (sheetUid, col, row) cell observing range
        """
        if not self.batchDbCtx:
            observerCellId = self._getCellId(*observer)
            if observerCellId is None:
                raise ValueError("non-existent observer cell")
            sheetId = self.getSheetId(sheetUid)[0]
            # add range to range table if necessary
            rangeId = self.insert("range", 'rangeId', {"observer": observerCellId, "sheetId": sheetId,
                                                       "ulCol": int(ulCol) - 1, 'ulRow': int(ulRow) - 1,
                                                       'lrCol': int(lrCol) - 1, 'lrRow': int(lrRow) - 1}, {})
        else:
            self.batchDbCtx.rangeinserts.append((self.getSheetId(sheetUid)[0], ulCol, ulRow, lrCol, lrRow, observer))



    def bulkSetRangeDeps(self,ranges):
        """ bulk load through the twisted connection pool """
        return self.dbpool.runInteraction(self._bulkSetRangeDepRunner,ranges)
        
    def _bulkSetRangeDepRunner(self,txn,ranges):
        """ bulk load a number of range dependencies """        
        txn.execute('insert into range (sheetId,ulCol,ulRow,lrCol,lrRow,observer) values %s ' % \
                 ','.join(['(%s,%s,%s,%s,%s,%s)' % \
                           (self.getSheetId(rng[0])[0],
                            int(rng[1])-1,int(rng[2])-1,int(rng[3])-1,int(rng[4])-1,
                            self.safeGetCellId(*rng[5])) for rng in ranges]))

    def deleteRangeDep(self, sheetUid, ulCol, ulRow, lrCol, lrRow, observer):
        """
        sheetUid: sheet containing range
        ulCol: upper left Column
        ulRow: upper left Row
        lrCol: lower right Column
        lrRow: lower right Row
        observer: a tuple: (sheetUid, col, row) cell observing range
        """
        observerCellId = self._getCellId(*observer)
        if observerCellId is None:
            raise ValueError("non-existent observer cell")
        sheetId = self.getSheetId(sheetUid)[0]

        wherecls = "observer = %d and sheetId = %d and " \
                   "ulCol = %d - 1 and ulRow = %d - 1 and lrCol = %d - 1 and lrRow = %d - 1" \
                   % (observerCellId, sheetId, ulCol, ulRow, lrCol, lrRow)

        if not self.batchDbCtx:
            self.sql("delete from range where %s" % wherecls)
        else:
            self.batchDbCtx.rangedeletions.append('(%s)' % wherecls)

    def clearRangeDeps(self, observer):
        """
        observer: a tuple: (observerSheetUid, observerCol, observerRow)
        blows out all Range deps for that observer
        """
        cellId = self._getCellId(*observer)
        if not cellId: return
        self.sql("delete from range where observer = %d" % cellId)

    def getRangesOnSheet(self, sheetUid):
        """
        return all the ranges ON a particular sheet.  Note, these
        aren't necessarily IN the same sheet.

        sheetId: Id of sheet

        returns: [[obsSheetUid, col, row, ulCol, ulRow, lrCol, lrRow]
                  ...]

        """
        return self.rsql("select obsSheet.sheetUid, cell.col + 1, cell.row + 1, ulCol + 1, ulRow + 1, lrCol + 1, lrRow + 1 "
                         "from cell, range, sheet as obsSheet, sheet "
                         "where cell.cellId = range.observer and "
                         "sheet.sheetId = range.sheetId and "
                         "obsSheet.sheetId = cell.sheetId and "
                         "sheet.sheetUid = '%s'" % sheetUid)

    ##
    ## Row and column mgmt
    ##
    def getCols(self, sheetUid):
        """returns a (colid, width, format) tuple for each column"""
        return self.rsql("select colid, width, col.format from col, sheet "
                         "where sheet.sheetUid = '%s' and col.sheetId = sheet.sheetId "
                         "order by colid" % sheetUid)

    def getCol(self, sheetUid, col):
        """ return a (colid, width, format) tuple for a particular column"""
        return self.rsql("select colid,width,col.format from col,sheet "
                         "where sheet.sheetUid = '%s' and col.sheetId = sheet.sheetId and col.colid = %d"
                         % (sheetUid, col))

    def getRows(self, sheetUid):
        """returns a (rowid, height, format) tuple for each row"""
        return self.rsql("select rowid, height, row.format from row, sheet "
                         "where sheet.sheetUid = '%s' and row.sheetId = sheet.sheetId "
                         "order by rowid" % sheetUid)

    def getRow(self, sheetUid, row):
        """ returns a (rowid, height, format) tuple for a particular row"""
        return self.rsql("select rowid, height, row.format from row,sheet "
                         "where sheet.sheetUid = '%s' and row.sheetId = sheet.sheetId and row.rowid = %d"
                         % (sheetUid, row))

    def setCol(self, sheetUid, colid, width, format):
        sheetId = self.getSheetId(sheetUid)[0]
        if self.batchDbCtx is None:        
            self.insertOrSet("col", {"sheetId": sheetId, "colid": int(colid)},
                             {"width": width, "format": self.escape(format)})
        else:
            self.batchDbCtx.colupdates.append(("('%s',%s,%s,'%s')" % (sheetId,int(colid),width,self.escape(format))))
            
    def setRow(self, sheetUid, rowid, height, format):
        sheetId = self.getSheetId(sheetUid)[0]
        if self.batchDbCtx is None:
            self.insertOrSet("row", {"sheetId": sheetId, "rowid": rowid},
                             {"height": height, "format": self.escape(format)})
        else:
            self.batchDbCtx.rowupdates.append(("('%s',%s,%s,'%s')" % (sheetId,int(rowid),height,self.escape(format))))

    def delCol(self,sheetUid,colid):
        #TODO: batchify
        sheetId = self.getSheetId(sheetUid)[0]        
        self.sql('delete from col where sheetId = %s and colid = %s',[sheetId,colid])

    def delRow(self,sheetUid,rowid):
        sheetId = self.getSheetId(sheetUid)[0]      
        self.sql('delete from row where sheetId = %s and rowid = %s',[sheetId,rowid])
        

    ##
    ## account management
    ##
    def getAccountByID(self,userID):
        if userID in self.authCache:
            return self.authCache[userID]
        else:
            userName = self.usql('select sz_user from account where id_acc = %s',[userID])
            return self.resolveAccount(userName,None,checkPassword=False)

        

    def userNameExists(self,userID):
        """ check the system for an existing account"""

        res = self.rsql("select id_acc from account where sz_user = '%s'" % (userID))
        return len(res) != 0

    def createAccount(self,userID,userHandle,password,locale,tz,existingsheets = None):
        """ create a Numbler account.  The initial state
        for the account is 0 (not verified).

        Existing sheets is used for upgrade purposes so we can add pending records
        for the old sheets
        """

        # all these properties should be checked by the calling layer
        if self.userNameExists(userID):
            raise AccountExists(userID)
        
        assert len(userID) > 0 and len(userHandle) > 0
        stateguid = guidbin()
        salt = guidbin()
        hash = sha.new(password)
        hash.update(salt)
        binpass = hash.digest()
        
        accountID = self.isql('insert into account (dt_crt,sz_user,sz_displayname,pass,' \
                              'acc_type,state,statetoken,salt,sz_locale,sz_tz) ' \
                              ' values ( UTC_TIMESTAMP(),%s,%s,%s,1,0,%s,%s,%s,%s) ',
                              [userID,userHandle,binpass,stateguid,salt,locale,tz])
        p = Principal(accountID,[])
        p.stateGUID = stateguid
        p.userid = userID
        p.displayname = userHandle

        if existingsheets:
            # existing sheets is a string of 16 digit sheet UIDs.
            guidlist = tuple([existingsheets[x:x+16] for x in range(0,len(existingsheets),16)])
            if len(guidlist) == 1:
                guidstr = "('%s')" % guidlist[0]
            else:
                guidstr = str(guidlist)
            
            self.sql('insert into acc_invite_pending (id_inviter, sheetId, sz_email) '\
                     'select 1, sheetId, "%s" from sheet where sheetUid in %s' % (userID,guidstr))

            return p,self.getSheetAliases(guidlist)

        else:
            return p,None


    def resolveAccount(self,userID,password,checkPassword = True):
        """
        resolve a principal by userID and sha-hashed password.
        the password must be in binary format (not base64 encoded)
        
        """
        
        result = self.rsql('select a.id_acc,a.sz_displayname,a.acc_type,a.state,a.api_id,a.api_key,a.statetoken,'\
                           'map.sheetId,map.owner,a.salt,a.pass,'\
                           'a.sz_locale,a.sz_tz '\
                           'from account a ' \
                           'LEFT OUTER JOIN acc_sheet_map map on map.id_acc = a.id_acc ' \
                           'where a.sz_user = %s',
                           [userID])
        if not len(result):
            raise AccountNotFound(userID)

        if checkPassword:
            # check the password
            hash = sha.new(password)
            hash.update(result[0][9])
            if hash.digest() != result[0][10]:
                # this isn't quite right - should be password mismatch
                raise AccountNotFound(userID)

        id_acc = result[0][0]
        if id_acc in self.authCache:
            return self.authCache[id_acc]

        p = Principal(
            # id_acc
            id_acc,
            # list of sheets
            [(res[7],res[8]) for res in result],
            # api_id
            result[0][4],
            # api_key
            result[0][5],
            # locale and timezone
            result[0][11],result[0][12])
        p.userid = userID
        p.displayname = result[0][1]
        p.setState(result[0][3],result[0][6])
        self.authCache[p.acc_id] = p
        if p.api_id and p.api_id in self.APIauthCache:
            self.APIauthCache[p.api_id] = p
        return p

    def resolveByStateToken(self,statetoken):
        """
        resolve an account by its state token.
        """
        assert len(statetoken) == 20

        result = self.rsql('select id_acc,sz_user,state from account where statetoken = %s',statetoken)
        if not len(result):
            raise AccountTokenNotExist

        acc_id,user,state = result[0]
        # check in cache
        if acc_id in self.authCache:
            return self.authCache[acc_id]
        else:
            return self.resolveAccount(user,None,False)


    def markAccountVerified(self,principal):
        """
        mark that an account is now verified
        """

        # this probably should use transactions and INNODB tables!!


        # if this is from a email address change:
        if principal.state == 2:
            self.sql('update account set sz_user = sz_pendinguser,sz_pendinguser = NULL, '\
                     'state = 1, statetoken = NULL where id_acc = %s',[principal.acc_id])
            principal.userid = self.usql('select sz_user from account where id_acc = %s',[principal.acc_id])
            principal.state = 1
        else:
            self.sql('update account set state = 1,statetoken = NULL where id_acc = %s',principal.acc_id)
            principal.state = 1            
            # move pending invites
            self.sql('insert into acc_sheet_map (id_acc,sheetId,owner) '
                     'select %s,p.sheetId,0 from acc_invite_pending p where p.sz_email = %s',
                     [principal.acc_id,principal.userid])
            # delete pending invites
            self.sql('delete from acc_invite_pending where sz_email = %s',[principal.userid])

            # update support.  if any of the pending invites is pending on a sheet owned
            # by the default account AND the sheet
            self.sql('update acc_sheet_map map1,acc_sheet_map map2 '\
                     'set map1.owner =1,map2.owner = 0 '\
                     'where map1.id_acc = %s and map2.id_acc = 1 '\
                     'and map1.sheetId = map2.sheetId and map2.owner = 1',[principal.acc_id])


        # reload the account to pick up the new sheets.
        if principal.acc_id in self.authCache:
            del self.authCache[principal.acc_id]        
        return self.resolveAccount(principal.userid,None,False)

    
    def createApiIdAndKey(self,principal):
        """
        create a key for use by web services.  An existing account is required.
        this should only be called by a principal
        """

        # run in seperate thread
        api_id,secretkey = alphaguid20(),guidbin()
        d = self.dbpool.runQuery('update account set api_id = %s, api_key = %s where id_acc = %s',
                 [api_id,secretkey,principal.acc_id])
        return api_id,secretkey,d

    def resolveApi(self,api_id):
        """
        resolve an account by api_id.  the return list is the account id, the secret key,
        and a list of authorized sheets
        """

        if api_id in self.APIauthCache:
            return self.APIauthCache[api_id]

        result = self.rsql('select a.id_acc,a.api_key,map.sheetId,map.owner,'\
                           'a.sz_user,a.sz_displayname,a.state,a.statetoken,'\
                           'a.sz_locale,a.sz_tz '\
                           'from account a ' \
                           'LEFT OUTER JOIN acc_sheet_map map on map.id_acc = a.id_acc ' \
                           'where a.api_id = %s',[api_id])
        if not len(result):
            raise AccountNotFound(api_id)

        # create a new principal
        newp = Principal(result[0][0],[(val[2],val[3]) for val in result],api_id,result[0][1],
                         result[0][8],result[0][9])
        newp.userid = result[0][4]
        newp.displayname = result[0][5]
        newp.setState(result[0][6],result[0][7])
        self.APIauthCache[api_id] = newp
        self.authCache[newp.acc_id] = newp
        return newp

    def addInvite(self,principal,sheetId,users):
        """
        invite a number of users to a sheet.  The principal is responsible
        for checking ownership of the sheet
        """
        userstr = ','.join(['"%s"' % (val) for val in users])
        existingaccs = self.rsql('select sz_user,sz_displayname,id_acc from account where sz_user in (%s)' % (userstr))
        existing = set([x[0] for x in existingaccs])

        new = set(users) - existing

        if len(existing):
            existingstr = ','.join(['"%s"' % (val) for val in existing])
            
            # add / update for existing accounts
            self.sql('insert into acc_sheet_map (id_acc,sheetId,owner) select id_acc,%s,0 from account '\
                     'where sz_user in (%s) ' \
                     'ON DUPLICATE KEY update acc_sheet_map.id_acc = account.id_acc' \
                     % (sheetId,existingstr))

            # update any cached principals
            for princp in [self.authCache[x[2]] for x in existingaccs if x[2] in self.authCache]:
                princp.addInvitedSheet(sheetId)

        if len(new):
            newinsert = ','.join(['(%d,%d,"%s")' % (principal.acc_id,sheetId,x) for x in new])
            self.sql('insert into acc_invite_pending (id_inviter,sheetId,sz_email) values %s' % (newinsert))


        # return the new users + information about existing users
        return new,[{u'username':unicode(x[0],'utf-8'),u'dispname':unicode(x[1],'utf-8')} for x in existingaccs]

    def revokeInvite(self,principal,sheetId,users):
        """
        revoke an invite from a sheet (or to be more precise, write permissions
        """
        if not len(users):
            return

        # verify that the principal is not in the revoke list
        if principal.userid in users:
            raise 'cannot revoke principal'
        
        userstr = ','.join(['"%s"' % (val) for val in users])
        existingaccs = self.rsql('select sz_user,id_acc,api_id from account where sz_user in (%s)' % (userstr))
        existing = set([x[0] for x in existingaccs])

        if len(existingaccs):
            self.sql('delete from acc_sheet_map where id_acc in (select id_acc from account where sz_user in (%s)) and sheetId = %s' \
                     % (userstr,sheetId))

            # notify any accounts in cache
            for princp in [self.authCache[x[1]] for x in existingaccs if x[1] in self.authCache]:
                princp.removeInvitedSheet(sheetId)
            for princp in [self.APIauthCache[x[2]] for x in existingaccs if x[2] in self.APIauthCache]:
                princp.removeInvitedSheet(sheetId)

        # delete from pending invites
        self.sql('delete from acc_invite_pending where sz_email in (%s) and sheetId = %s' % (userstr,sheetId))
                    

    def removeInvitedSheet(self,principal,sheetId):
        """
        remove a principal from a sheet that they were invited to.
        this method will do nothing if the sheetId is not associated with the account.
        """
        return self.dbpool.runQuery('delete from acc_sheet_map where id_acc = %s and sheetId = %s and owner = 0',
                 [principal.acc_id,sheetId])

        

##    def getInvitesForSheet(self,sheetId):
##        """
##        fetch invites for a sheet
##        """

##        return self.rsql('select sz_user,1 from account a ' \
##                  'inner join acc_sheet_map map on map.id_acc = a.id_acc AND map.sheetId = %s ' \
##                  'UNION select sz_email,0 from acc_invite_pending where sheetId = %s',
##                  [sheetId,sheetId])

    def requestPasswordChange(self,userID):
        """
        request a password change token.  raises a account not found exception
        if the token does not exist
        """

        state = self.usql('select state from account where sz_user = %s',[userID])
        if state is None:
            raise AccountNotFound(userID)
        elif state == 0:
            raise AccountNotVerified()

        token = sha.new(guidbin()).digest()
        self.sql('update account set statetoken=%s,statetoken_dtcrt=UTC_TIMESTAMP() '\
                            'where sz_user = %s',[token,userID])
        return token
        
    def resolvePasswordChange(self,token):
        """
        resolve an account by the security token and return the principal.

        token should be a binary SHA hash
        """

        validstate = 1
        expireminutes = 30
        assert len(token) == 20

        result = self.rsql('select sz_user,id_acc from account where state = %s and statetoken = %s ' \
                  'AND (TIME_TO_SEC(UTC_TIMESTAMP()) - TIME_TO_SEC(statetoken_dtcrt))/60 ' \
                  '<= %s',
                  [validstate,token,expireminutes])
        if not len(result):
            raise PasswordChangeTokenExpire()

        else:
            user,id_acc= result[0]
            if id_acc in self.authCache:
                del self.authCache[id_acc]                  
            return self.resolveAccount(user,None,False)

    def updatePassword(self,principal,passwd):
        """
        update the password for an account.  the password must be
        a binary SHA hash.

        any pending change password tokens will be invalidated after an update
        
        """
        salt = guidbin()
        hash = sha.new(passwd)
        hash.update(salt)
        pdigest = hash.digest()
        self.sql('update account set pass = %s,salt = %s, statetoken = NULL where id_acc = %s',
                 [pdigest,salt,principal.acc_id])
        


    def getAccountSheetSummary(self,principal):
        """
        return a summary of properties 
        """
        return self.dbpool.runQuery('select map.sheetId,sa.alias,sheet.type,'\
                         'COUNT(DISTINCT(map2.id_acc)) invites,'\
                         'count(p.sz_email) pending, sheet.sheetUid,map.owner '\
                         'from sheetalias sa '\
                         'INNER JOIN acc_sheet_map map on map.id_acc = %s and sa.sheetId = map.sheetId and map.owner =1 '\
                         'INNER JOIN sheet on sheet.sheetId = map.sheetId '\
                         'LEFT OUTER JOIN acc_sheet_map map2 on map2.sheetId = map.sheetId and map2.owner = 0 AND map2.id_acc <> 1 '\
                         'LEFT OUTER JOIN acc_invite_pending p on p.sheetId = map.sheetId GROUP BY (map.sheetId) '\
                         'UNION '\
                         'select map.sheetId,sa.alias,sheet.type,0,0,sheet.sheetUid,map.owner '\
                         'from acc_sheet_map map '\
                         'INNER JOIN sheet on sheet.sheetId = map.sheetId '\
                         'INNER JOIN sheetalias sa on sa.sheetId = map.sheetId '\
                         'where map.id_acc = %s and map.owner = 0',
                         [principal.acc_id,principal.acc_id])

    def getUserListForSheet(self,sheetId):
        """
        get a detailed list of the current users on a sheet
        """

        return self.dbpool.runQuery('select acc.sz_user,sz_displayname,FALSE from acc_sheet_map map '\
                         'INNER JOIN account acc on acc.id_acc = map.id_acc '\
                         'where sheetId = %s and owner = 0 and acc.id_acc <> 1 UNION '\
                         'select sz_email,sz_email,TRUE from acc_invite_pending where sheetId = %s',[sheetId,sheetId])
    

    def modifyAccount(self,principal,args):
        return self.dbpool.runInteraction(self._modifyAccountInternal,principal,args)

    def _modifyAccountInternal(self,txn,principal,args):
        """
        perform updates to account properties all at once.  this is slightly
        broken because code is duplicated from other places (password changes most notably)

        this function can update the password, nick, and email address.
        """

        ret = {}
        setargs = []
        queryargs = []
        

        passwd = args.get('passwd')
        if passwd:
            salt = guidbin()
            hash = sha.new(passwd)
            hash.update(salt)
            pdigest = hash.digest()
            setargs += ('pass = %s','salt = %s','statetoken = NULL')
            queryargs += (pdigest,salt)
            #txn.execute('update account set pass = %s,salt = %s,statetoken = NULL where id_acc = %s',
            #           [pdigest,salt,principal.acc_id])
            

        newemail = args.get('email')
        if newemail:
            txn.execute('select id_acc from account where sz_user = %s',[newemail])
            values = txn.fetchall()
            if len(values):
                raise AccountExists
            token = sha.new(guidbin()).digest()            
            setargs += ('state=2','statetoken=%s','sz_pendinguser = %s')
            queryargs += (token,newemail)
            #txn.execute('update account set state=2,statetoken=%s,sz_pendinguser = %s '\
            #                                 'where id_acc = %s',[token,newemail,principal.acc_id])
            ret['newemailtoken'] = token
            ret['newemail'] = newemail
            
        nick = args.get('dispname')
        if nick:
            setargs.append('sz_displayname = %s')
            queryargs.append(nick)
            #txn.execute('update account set sz_displayname = %s where id_acc = %s',[nick,principal.acc_id])
            ret['nick'] = nick

        tz = args.get('tz')
        if tz:
            setargs.append('sz_tz = %s')
            queryargs.append(tz)
            ret['tz'] = tz
        locale = args.get('locale')
        if locale:
            setargs.append('sz_locale = %s')
            queryargs.append(locale)
            ret['locale'] = locale
        # save to db
        if len(queryargs):
            queryargs.append(principal.acc_id)
            txn.execute('update account set %s where id_acc = %%s' % ','.join(setargs),queryargs)
        return ret
    
    def clear(self):
        self.sql("delete from sheet")
        self.sql("delete from sheetalias")
        self.sql("delete from dep")
        self.sql("delete from range")
        self.sql("delete from cell")
        self.sql("delete from col")
        self.sql("delete from row")

    def newbatchDbCtx(self):
        self.batchDbCtx = BatchDbCtx(self)
        return self.batchDbCtx

    def clearBatchDbCtx(self):
        del self.batchDbCtx
        self.batchDbCtx = None


    # bulk operation (delete and insert)
    def doBulkOperation(self,batchCtx):
        d = self.dbpool.runInteraction(self._bulkOperation,batchCtx)
        return d

    def _bulkOperation(self,txn,batchCtx):
        if len(batchCtx.rangedeletions):
            #print 'bulkDelete: deleting from range'
            rangestr = 'delete from range where %s' % 'or'.join(batchCtx.rangedeletions)
            txn.execute(rangestr)
        if len(batchCtx.depdeletions):
            #print 'bulkDelete: deleting from dep'
            depstr = 'delete from dep where %s' % 'or'.join(batchCtx.depdeletions)
            txn.execute(depstr)
        if len(batchCtx.celldeletes):
            #print 'bulkDelete: deleting from cell',batchCtx.celldeletes
            delstr = 'delete from cell where %s' % 'or'.join(batchCtx.celldeletes)
            txn.execute(delstr)
        if len(batchCtx.cellupdates):
            updatestr = 'insert into cell (sheetId,col,row,formula,format) values %s '\
                        'ON DUPLICATE KEY update formula=VALUES(formula),format=VALUES(format)' % \
                        ','.join(batchCtx.cellupdates)
            #print 'bulkDelete: updating cell',updatestr
            txn.execute(updatestr)

        # insert the cell dependencies
        if len(batchCtx.depinserts):
            # make sure the new cellId's exist
            txn.executemany('insert IGNORE into cell (sheetId,col,row,formula,format) values '\
                            '(%s,%s,%s,"","")',[(x[0],x[2][1]-1,x[2][2]-1) for x in batchCtx.depinserts])
            #print 'about to load dependencies:',batchCtx.depinserts
            txn.executemany('insert into dep select cell1.cellId,cell2.cellId from '\
                            'cell cell1, cell cell2 '\
                            # observered
                            'where cell1.sheetId = %s and cell1.col = %s and cell1.row = %s '\
                            #observer
                            'and cell2.sheetId = %s and cell2.col = %s and cell2.row = %s',
                            ((x[0],x[2][1]-1,x[2][2]-1,x[1],x[3][1]-1,x[3][2]-1)
                             for x in batchCtx.depinserts))
            

        # insert the range dependencies
        if len(batchCtx.rangeinserts):
            txn.executemany('insert into range (observer,sheetId,ulCol,ulRow,lrCol,lrRow) '\
                            'select cellId,%s,%s,%s,%s,%s from cell '\
                            'where sheetId = %s and col = %s and row = %s',
                            ((int(x[0]),int(x[1])-1,int(x[2])-1,int(x[3])-1,int(x[4])-1,int(x[0]),
                              int(x[5][1])-1,int(x[5][2])-1)
                             for x in batchCtx.rangeinserts))
        if len(batchCtx.rowupdates):
            print 'executing rowupdates',batchCtx.rowupdates
            txn.execute("insert into row (sheetId,rowid,height,format) values %s "
                        "ON DUPLICATE KEY update height=VALUES(height),format=VALUES(format)"
                        % ','.join(batchCtx.rowupdates))

        if len(batchCtx.colupdates):
            print 'executing colupdates',batchCtx.colupdates
            txn.execute("insert into col (sheetId,colid,width,format) values %s "
                        "ON DUPLICATE KEY update width=VALUES(width),format=VALUES(format)"
                        % ','.join(batchCtx.colupdates))


    def addColFindChangeCells(self,sheetH,colID,numberOfCols):
        """
        find the affected cells for a column add operation.
        """
        return self.dbpool.runInteraction(self._addColFindChangeCells,self.getSheetId(str(sheetH))[0],colID,numberOfCols)

    def _addColFindChangeCells(self,txn,sheetId,colID,numberOfCols):

        if numberOfCols > 0:
            # verify that there is not any cell in the last col.
            txn.execute('select cellId from cell where sheetId = %s and col >= %s '\
                        'and not (formula = "" and format = "")',[sheetId,Col.getMax() - numberOfCols])
            res = txn.fetchall()
            if len(res):
                raise ExpansionOverflow()

        # find all the cells that are >= the target column.  Columns are
        # always inserted before the target row.
        # we *could* fetch all the cell informatio in case we need it to avoid doing lots of DB lookups.
        print '_addColFindChangeCells called with ',sheetId,colID
        txn.execute(
            #and range.ulCol >= %s 
            'select distinct(cellId),col+1,row+1 from cell '\
            'LEFT OUTER JOIN range on range.sheetId = %s and %s <= range.lrCol '\
            'where (col >= %s or cellId = observer) AND cell.sheetId = %s '\
            'AND not (formula = "" and format = "") '\
            'UNION '\
            'SELECT distinct(cell2.cellId),cell2.col+1,cell2.row+1 from cell cell1 '\
            'INNER JOIN dep on dep.observed = cell1.cellID '\
            'INNER JOIN cell cell2 on cell2.cellId = dep.observer and cell2.sheetId = %s '\
            'where cell1.col >= %s AND cell1.sheetId = %s',
                    [sheetId,colID-1,colID-1,#colID-1,
                     sheetId,sheetId,colID-1,sheetId])
        return txn.fetchall()

    def addRowFindChangeCells(self,sheetH,rowID,numberOfRows):
        return self.dbpool.runInteraction(self._addRowFindChangeCells,self.getSheetId(str(sheetH))[0],rowID,numberOfRows)

    def _addRowFindChangeCells(self,txn,sheetId,rowID,numberOfRows):

        if numberOfRows > 0:
            txn.execute('select cellId from cell where sheetId = %s and row >= %s '\
                        'and not (formula = "" and format = "")',[sheetId,Row.getMax() - numberOfRows])
            res = txn.fetchall()
            if len(res):
                raise ExpansionOverflow()

        # find all the cells that are >= the target column.  Columns are
        # always inserted before the target row.
        # we *could* fetch all the cell informatio in case we need it to avoid doing lots of DB lookups.
        
        txn.execute(
            #'select cellId,col,row,formula,formula from cell '\
            'select distinct(cellId),col+1,row+1 from cell '\
            'LEFT OUTER JOIN range on range.sheetId = %s and %s <= range.lrRow '\
            'where (row >= %s or cellId = observer) AND cell.sheetId = %s '\
            'AND not (formula = "" and format = "") '\
            'UNION '\
            'SELECT distinct(cell2.cellId),cell2.col+1,cell2.row+1 from cell cell1 '\
            'INNER JOIN dep on dep.observed = cell1.cellID '\
            'INNER JOIN cell cell2 on cell2.cellId = dep.observer and cell2.sheetId = %s '\
            'where cell1.row >= %s AND cell1.sheetId = %s',
            [sheetId,rowID-1,rowID-1,sheetId,sheetId,rowID-1,sheetId])
        return txn.fetchall()        


    #
    # remote transaction management
    #

    def addWsTransaction(self,sheetUid,rowId,colId,expiration=30):
        sheetId = self.getSheetId(sheetUid)[0]
        return self.dbpool.runInteraction(self._addWsTransaction,sheetId,rowId,colId,expiration)

    def _addWsTransaction(self,txn,sheetId,rowId,colId,expiration):

        # insert a new transaction.
        try:
            txn_id = self._insertWsTxn(txn,sheetId,rowId,colId,expiration)
        except db.IntegrityError,e:
            if e.args[0] == 1062: # integrity error
                # delete the transaction
                self._clearWsTxn(txn,sheetId,rowId,colId)
                txn_id = self._insertWsTxn(txn,sheetId,rowId,colId,expiration)
        return txn_id

        # if an existing transaction exists we will get a duplicate key error.   
    def _insertWsTxn(self,txn,sheetId,rowId,colId,expiration):
        txn.execute('insert into remote_txn (dt_expire,sheetId,colid,rowid) values '\
                    '(ADDTIME(UTC_TIMESTAMP(),%s),%s,%s,%s)',
                    [expiration,sheetId,rowId,colId])
        # this is necessary because insert_id is on the connect object
        # and is not part of the DBAPI standard.
        return txn._connection._connection.insert_id()
                    

    def _clearWsTxn(self,txn,sheetId,rowId,colId):
        txn.execute('delete from remote_txn where sheetId = %s and rowId = %s and colId = %s',
                    [sheetId,rowId,colId])

    def resolveWsTransaction(self,txn_id):
        return self.dbpool.runInteraction(self._resolveWsTransaction,txn_id)

    def _resolveWsTransaction(self,txn,txn_id):
        """
        look a transaction from the database.  If the transaction has
        expired raise an error message.
        """
        txn.execute('select dt_expire,sheetId,colid, rowid, '\
                    'UTC_TIMESTAMP() ctime '\
                    'from remote_txn where txnId = %s',[txn_id])
        result = txn.fetchall()
        if len(result) == 0:
            raise RemoteWsTxnNotFound(txn_id)
        if result[0][0] < result[0][4]:
            raise RemoteWsTxnExpired(txn_id)
        return result[0][1],result[0][2],result[0][3]
        
    def purgeSheetWsTransactions(self,sheetUid):
        """
        this is mostly a utility class for cleaning up after a test.
        """
        self.sql('delete from remote_txn where sheetId = %s',
                 [self.getSheetId(sheetUid)[0]])

    def getTxnIdRange(self,rangesize=100):
        """ get a range of transaction Ids.  this information lives in the
        database so that in case of server restart we aren't resusing Ids """

        rngid = self.isql('insert into txn_ids (req_start,req_end) select IFNULL(max(req_end),0)+1, '\
                  'IFNULL(max(req_end),0)+%s  from txn_ids',[rangesize])
        return self.rsql('select req_start,req_end from txn_ids where id_request = %s',[rngid])[0]

            
class BatchDbCtx(object):
    """
    batch up a number of database requests for big operations like, move, paste,
    adding rows and columns, etc.
    """

    def __init__(self,ssdb):
        self.ssdb = ssdb
        self.rangedeletions = []
        self.depdeletions = []
        self.celldeletes = []
        self.cellupdates = []
        self.depinserts = []
        self.rangeinserts = []
        self.rowupdates = []
        self.colupdates = []

    def save(self):
        # create a new asynchronous database request
        d =  self.ssdb.doBulkOperation(self)
        d.addBoth(self.onDone)
        d.addErrback(self.errHandler)
        return d

    def onDone(self,arg):
        self.ssdb.clearBatchDbCtx()
        return arg


    def errHandler(self,arg):
        print 'error occured during batch operation:',arg
        return arg

def main():

    import sys
    cmd = sys.argv[1]

    if cmd == '-u':
        print 'usage: ssdb cmd'
        return
    
    if cmd == 'newdb':
        bdb = ssInit.getInstance()
        bdb.buildDB()
        return

    import engine
    eng = engine.Engine.getInstance()
    bdb = eng.ssdb
    bdb.verbose = 1
    
    if cmd == 'init':
        bdb.dropTables()
        bdb.createTables()
        bdb.createIndices()
        bdb.createDefaultEntries()

    elif cmd == 'test':
        bdb.setRangeDep("booya", 1, 1, 3, 3, ("dookie", 4, 1))
        print bdb.getRangesOnSheet("booya")
    else:
        print 'Error: bad command: ' + cmd

if __name__ == '__main__': main()
