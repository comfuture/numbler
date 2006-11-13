#!/usr/bin/env python

from numbler.sdk import api
import random,time


#apiID = 'phtzngMIkslQrltJacTw'
#secretkey = 'D1F36C42973FBEACD9A4C4F039048F6016BA4699'
#UID = 'sflhgTkIpwIcmJtv'

apiID = 'NMADlTFkYmWwKjsTmdAv'
secretkey = '69EB23A63093FB24E36272CFB35D6CC6204C2FFB'
UID = '0d8GWdQOexKAhgIg'

def randomint():
    return random.randint(0,5000)

def quotedstr():
    return """quo'ted" st''ri"ngs"""

def imgs():
    return 'http://www.google.com/intl/en/images/logo.gif'

def randomcells(mygen):
    
    con = api.NumblerConnection(UID,apiID,secretkey)
    
    colrange = map(chr,range(65,91))
    rowrange = range(1,40)
    
    for i in range(0,100):
        updater = con.newCellUpdater()
        for j in range(0,5):
            updater.addCell(random.choice(colrange),random.choice(rowrange),mygen())
        con.sendCells(updater)
        time.sleep(1)

randomcells(quotedstr)
#randomcells(imgs)
#randomcells(randomint)
