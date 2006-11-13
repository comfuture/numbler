#!/usr/bin/env python

import unittest
from numbler.server import sheet,parser,engine,cell
from numbler.server.colrow import Col,Row
from numbler.server.exc import *

eng = engine.Engine.getInstance()
import sha
from numbler.server.sslib.utils import alphaguid16,alphaguid20

class accountTestCase(unittest.TestCase):
    """ supports operations on temporary sheets"""

    def getNewUser(self):
        guid = alphaguid16() + '@numbler.com'
        return guid,sha.new(guid).digest()

    def test1CreateAccount(self):
        """
        create a random account
        """
        print 'first test called!'

        acc,passwd = self.getNewUser()
        p,changesheets = eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')
        self.failUnless(p.acc_id > 0)
        self.acc1principal = eng.ssdb.resolveAccount(acc,passwd)
        self.failUnless(self.acc1principal.acc_id == p.acc_id)
        

    def test2CantCreateDuplicateAccount(self):
        """ verify that a duplicate account can not be created """
        e = None
        acc,passwd = self.getNewUser()
        eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')
        try:
            eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')
        except AccountExists,e:
            pass
        self.failUnless(isinstance(e,AccountExists))
        

    def test3VerifyAccount(self):
        """ test a positive case for verifing an account by a guid """
        acc,passwd = self.getNewUser()
        principal,changedsheets = eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')

        newp = eng.ssdb.resolveByStateToken(principal.stateGUID)
        newp = eng.ssdb.markAccountVerified(newp)
        self.failUnless(newp.state == 1)
        self.failUnless(newp.stateGUID is None)
        

    def test4BadStateToken(self):
        """ test that a bad state token will cause an error """
        from numbler.server.sslib.utils import guidbin
        newtoken = guidbin()
        e = None
        try:
            eng.ssdb.resolveByStateToken(newtoken)
        except AccountTokenNotExist,e:
            pass
        self.failUnless(isinstance(e,AccountTokenNotExist))

    def test5InviteExistingUser(self):
        """ test inviting an existing numbler user to a spreadsheet"""
        acc,passwd = self.getNewUser()
        p1,changedsheets = eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')
        acc2,passwd2 = self.getNewUser()
        p2,changesheets = eng.ssdb.createAccount(acc2,acc2,passwd2,'en_US','America/Chicago')

        shtUid = alphaguid16()
        eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet',p1)

        self.failUnless(len(p1.ownedsheets) == 1)
        shtId = list(p1.ownedsheets)[0]

        p1.inviteToSheet(shtId,[acc2])
        self.failUnless(len(p2.sheets) == 1)
        self.failUnless(list(p2.sheets)[0] == shtId)


    def test6InviteNewUser(self):
        """
        test inviting a non existing user to a spreadsheet. This test
        verifies that once the new account is created any pending invited sheets
        are propagated over to the new account.

        the following flow is simulated:

        user A creates a new spreadsheet
        user A invites B to A.
        B is not an existing user
        B goes to the web site and creates an account.
        B creates account
        B clicks on verification email in link.

        """
        acc,passwd = self.getNewUser()
        p1,changedsheets = eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')
        acc2,passwd2 = self.getNewUser()

        shtUid = alphaguid16()
        eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet',p1)

        self.failUnless(len(p1.ownedsheets) == 1)
        shtId = list(p1.ownedsheets)[0]

        p1.inviteToSheet(shtId,[acc2])
        p2,changesheets = eng.ssdb.createAccount(acc2,acc2,passwd2,'en_US','America/Chicago')
        p2 = eng.ssdb.markAccountVerified(p2)
        self.failUnless(len(p2.sheets) == 1)
        self.failUnless(list(p2.sheets)[0] == shtId)

    def test7MultiInvite(self):
        """
        test inviting multiple people to the spreadsheet
        """
        acc,passwd = self.getNewUser()
        p1,changedsheets = eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')

        shtUid = alphaguid16()
        eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet',p1)
        shtId = list(p1.ownedsheets)[0]
        
        invites = [self.getNewUser() for x in range(1,5)]
        emails = [x[0] for x in invites]

        p1.inviteToSheet(shtId,emails)
        newaccs = []
        
        for invite in invites:
            p = eng.ssdb.markAccountVerified(eng.ssdb.createAccount(invite[0],invite[0],invite[1])[0],'en_US','America/Chicago')
            newaccs.append(p)
            self.failUnless(shtId in p.sheets)

        revokemails = [invites[x][0] for x in range(3)]
        p1.revokeInvite(shtId,revokemails)
        for invite,existingacc in [(invites[x],newaccs[x]) for x in range(3)]:
            self.failUnless(shtId not in existingacc.sheets)            
            p = eng.ssdb.resolveAccount(invite[0],invite[1])
            self.failUnless(shtId not in p.sheets)


    def test8InviteToNonOwnedSheet(self):
        """
        test inviting to a sheet that we don't own
        """
        acc,passwd = self.getNewUser()
        p1,changedsheets = eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')

        shtUid = alphaguid16()
        eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet',p1)
        shtId = list(p1.ownedsheets)[0]

        acc2,passwd2 = self.getNewUser()
        p2,changedsheets = eng.ssdb.createAccount(acc2,acc2,passwd2,'en_US','America/Chicago')
        e = None
        try:
            p2.inviteToSheet(shtId,'foo@numbler.com')
        except AccountAuthFailure,e:
            print e
        self.failUnless(isinstance(e,AccountAuthFailure))

    def test9ResolveNonExistantAccount(self):
        """
        attempt to resolve a non existing account
        """
        e = None
        try:
            eng.ssdb.resolveAccount(*self.getNewUser())
        except AccountNotFound,e:
            print e
        self.failUnless(isinstance(e,AccountNotFound))
        

    def test11ListInvitedSheets(self):
        """
        verify that principal's owned sheets
        don't contain invited sheets
        """
        pass
        acc,passwd = self.getNewUser()
        p1 = eng.ssdb.markAccountVerified(eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')[0])
        shtUid = alphaguid16()
        id = eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet',p1)
        self.failUnless(id in p1.ownedsheets)

        acc,passwd = self.getNewUser()
        p2 = eng.ssdb.markAccountVerified(eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')[0])
        shtUid = alphaguid16()
        p2_id1 = eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet2',p2)
        shtUid = alphaguid16()
        p2_id2 = eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet3',p2)        

        p2.inviteToSheet(p2_id1,[p1.userid])
        p2.inviteToSheet(p2_id2,[p1.userid])                         
        self.failUnless(p2_id1 in p2.ownedsheets and p2_id2 in p2.ownedsheets)
        self.failUnless(p2_id1 in p2.sheets and p2_id2 in p2.sheets)
        self.failUnless(p2_id1 in p1.sheets and p2_id2 in p1.sheets)
        self.failUnless(p2_id1 not in p1.ownedsheets and p2_id2 not in p1.ownedsheets)
        

    def test12RenameSheet(self):
        """
        test renaming a sheet
        """
        acc,passwd = self.getNewUser()
        p1 = eng.ssdb.markAccountVerified(eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')[0])
        shtUid = alphaguid16()
        id1 = eng.ssdb.setSheetAlias(shtUid,'unittest invite sheet2',p1)
        name = 'and now for something completely different'
        p1.renameSheet(id1,'and now for something completely different')
        newname = eng.ssdb.getSheetAlias(shtUid)
        self.failUnless(newname == name)
        

    def createNewSheet(self):
        """ create a new sheet """
        pass

    def test14RequestPasswordReset(self):
        """
        request a password reset based on the user's email.
        Resolve the account by the reset token and change the password.
        """
        acc,passwd = self.getNewUser()
        eng.ssdb.markAccountVerified(eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')[0])

        token = eng.ssdb.requestPasswordChange(acc)
        principal = eng.ssdb.resolvePasswordChange(token)
        newpasswd = sha.new('new password').digest()
        eng.ssdb.updatePassword(principal,newpasswd)


    def test15RequestPasswordResetNoAcount(self):
        """
        request a password reset for a non existing account.
        """
        acc,passwd = self.getNewUser()
        e = None
        try:
            eng.ssdb.requestPasswordChange(acc)
        except AccountNotFound,e:
            pass

        self.failUnless(isinstance(e,AccountNotFound))
        

    def test16RequestPasswordResetExpire(self):
        """
        test attempting to reset a the password and then
        use an expired reset token
        """
        acc,passwd = self.getNewUser()
        p1 = eng.ssdb.markAccountVerified(eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')[0])
        token = eng.ssdb.requestPasswordChange(acc)

        # do something slightly wrong here - modify the token timestamp
        # so this will fail.
        eng.ssdb.sql('update account set statetoken_dtcrt = 0 where id_acc = %s',p1.acc_id)
        e = None
        try:
            principal = eng.ssdb.resolvePasswordChange(token)
        except PasswordChangeTokenExpire,e:
            pass
        self.failUnless(isinstance(e,PasswordChangeTokenExpire))
        
    
    def test18CreateApiAcount(self):
        """
        test that an acocunt with an API key can be resolved
        """
        acc,passwd = self.getNewUser()
        p1 = eng.ssdb.markAccountVerified(eng.ssdb.createAccount(acc,acc,passwd,'en_US','America/Chicago')[0])
        p1.registerForApiAccount()
        self.failUnless(p1.api_id is not None)
        self.failUnless(p1._secret_key is not None)

        # check that second request returns false
        self.failUnless(not p1.registerForApiAccount())

        p2 = eng.ssdb.resolveApi(p1.api_id)

    def test19ResolveByApiFailure(self):
        """
        test that a bad API key will fail to resolve
        """
        testguid = alphaguid20()
        e = None
        try:
            eng.ssdb.resolveApi(testguid)
        except AccountNotFound,e:
            print e

        self.failUnless(isinstance(e,AccountNotFound))
        self.failUnless(e.userID == testguid)


    def testMakeSheetPublic(self):
        """
        test making a sheet public
        """
        pass

    def testMakeSheetPrivate(self):
        """
        test converting a public sheet to a private sheet
        """
        pass

    def testMakingNowOwnedSheetPrivate(self):
        """
        yeah.
        """
        pass


    def testDeleteSheet(self):
        """
        test deleting a sheet (must be owner)
        """
        pass

    def testCreateSheet(self):
        """
        test creating a sheet

        should test the ability to create a new spreadsheet.
        should test the failure to create a spreadsheet with the same name
        """
        pass

    def testRevokePendingInvite(self):
        """
        test revoking a pending invite
        """
        pass
    
    def testChangePassword(self):
	"""
	test changing the password on an account
	"""
	pass

suite = unittest.makeSuite(accountTestCase)

def main():
    t = unittest.TextTestRunner()
    t.run(suite)


if __name__ == '__main__': main()
