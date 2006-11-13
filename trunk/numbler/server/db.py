# (C) Numbler LLC 2006
# See LICENSE for details.

##
##
## db.py
##
## Handles database access
##
##

import MySQLdb, re, string
from sslib import singletonmixin
from _mysql_exceptions import IntegrityError

# support for deferred db results
from twisted.enterprise import adbapi

class Db(singletonmixin.Singleton):

    def __init__(self, user, passwd, log=None):
        self.dbc = MySQLdb.connect(host='localhost', user=user,
                                   passwd=passwd, db = self.db) 
        self.cursor = self.dbc.cursor()
        self.log = log

        self.dbpool = adbapi.ConnectionPool("MySQLdb",host="localhost",
                                            user=user,passwd=passwd,db=self.db)

    def escape(self, str):
        return MySQLdb.escape_string(str)
        #"""escapes string for SQL"""
        #return re.sub('\'', '\\\'', str)

    def sql(self, operation,args=None):
        """execute operation...returns nothing"""
        if self.log: self.log.info(operation)
        return self.cursor.execute(operation,args)

    def rsql(self, operation,args=None):
        """returns all results"""
        self.sql(operation,args)
        return self.cursor.fetchall()

    def osql(self, operation,args=None):
        """returns single row"""
        self.sql(operation,args)
        return self.cursor.fetchone()

    def usql(self, operation,args=None):
        """returns single result if extant, None otherwise"""

        ret = self.osql(operation,args)
        if ret is None: return None

        if len(ret) > 0:
            return ret[0]
        else:
            return None

    def isql(self, operation,args=None):
        """used for inserts -- returns index of newly inserted row"""
        self.sql(operation,args)
        return self.dbc.insert_id()

    def insertOrSet(self, table, selDict, setDict):
        """insert or set values on table.  inserts if row does not yet exist.
        selDict: dictionary of names and values to select on
        setDict: dictionary of names and values to set, in addition to those in selDict

        Note: this could rewritten using the proprietary MySQL syntax ON DUPLICATE KEY or
        perhaps using  a sproc with other databases
        """

        if len(setDict) > 0:
            insStr = "insert into %s (%s) values (%s) ON DUPLICATE KEY update %s " % \
                     (table, ", ".join(selDict.keys() + setDict.keys()),
                      ",".join(["'%s'" % x for x in selDict.values() + setDict.values()]),
                      ", ".join(["%s = '%s'" % (x, y) for x, y in setDict.iteritems()]))
            return self.isql(insStr)
        else:
            try:
                insStr = "insert into %s (%s) values (%s)" % \
                         (table, ", ".join(selDict.keys() + setDict.keys()),
                          ", ".join(["'%s'" % x for x in selDict.values() + setDict.values()]))
                return self.isql(insStr)
            except IntegrityError,e:
                # integrity errors are ok in this case.
                if e.args[0] != 1062:
                    raise e
                
    def insert(self, table, priKey, selDict, insDict):
        """inserts if not already extant
        priKey: primary key.  if None, uses selDict
        selDict: dictionary of names and values to select on
        insDict: dictionary of names and values to insert, in addition to those in selDict
        """

        selCrit = " and ".join(["%s = '%s'" % (x, y) for x, y in selDict.iteritems()])
        selItems = priKey or ", ".join(selDict.keys())
        selStr = "select %s from %s where %s" % (selItems, table, selCrit)
        ret = self.usql(selStr)
        if ret is None:
            insStr = "insert into %s (%s) values (%s)" % \
                     (table, ", ".join(selDict.keys() + insDict.keys()),
                      ", ".join(["'%s'" % x for x in selDict.values() + insDict.values()]))
            ret = self.isql(insStr)
        return ret

    def executeMany(self, operation, data):
        self.cursor.executemany(operation, data)

    ##
    ## Table and index management
    ## 
    ## Set tables in derived clas as follows
    ##  tables = {
    ##   'tb1':    # table name
    ##    [['lid', 'integer unsigned not null primary key auto_increment'],
    ##     ['username', 'tinytext', 8]],        # 3rd argument: 'idx' for index, number for index of given length, or primary key spec
    ##
    ##   'localluser':
    ##  [['lid', 'integer unsigned not null', 'idx'],
    ##  ['password', 'tinytext'],
    ##   ...
    ##   ] }
    ##

    def createTables(self):
        for table in self.tables.keys():
            self.createTable(table)

    def createTable(self, table):
        if self.log: self.log.info('Db.createTable(): creating table \'%s\'' % table)
        typespec = string.join(map(lambda x: '%s %s' % tuple(x[:2]), self.tables[table]), ', ')
        cstr = 'create table ' + table + ' (' + typespec + ')'
        self.sql(cstr)

    def createIndices(self):
        for table in self.tables.keys():
            self.createIndex(table)

    def createIndex(self, table):
        for pair in filter(lambda x: len(x) == 3, self.tables[table]):
            if pair[2] == 'idx':
                ispec = pair[0]
            else:
                ispec = pair[0] + '(' + pair[2] + ')'
            cstr = 'create index %s_%s on %s (%s)' % (table, pair[0], table, ispec)
            self.sql(cstr)

    def dropIndices(self):
        for table in self.tables.keys():
            self.dropIndex(table)

    def dropIndex(self, table):
        for pair in filter(lambda x: len(x) == 3, self.tables[table]):
            cstr = 'drop index %s_%s on %s' % (table, pair[0], table)
            self.sql(cstr)

    def dropTables(self):
        for table in self.tables.keys():
            if self.log: self.log.info('Dropping table \'%s\'' % table)
            try:
                self.sql('drop table %s' % table)
            except MySQLdb.OperationalError:
                if self.log: self.log.info("No table \'%s\' to drop" % table)

    def clearTable(self, table):
        self.sql("delete from %s" % table)
