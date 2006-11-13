# (C) Numbler LLC 2006
# See LICENSE for details.

##
## Spreadsheet Exceptions
##

# Excel to Python errors mapping

class SSError(ValueError):

    errDesc = 'unknown error'

    def __init__(self,*args):
        if not len(args):
            ValueError.__init__(self,self.errDesc)
        else:
            ValueError.__init__(self,*args)

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    def __str__(self):
        return self.ErrStr

    def getR1C1(self, relCellH):
        return self.ErrStr

    def eval(self,stackvalue):
        raise self

# #DIV/0!  The formula or function is trying a division by 0. Which is
# mathematically undetermined. Check for values = 0. One of the
# references in the formula may be to a blank or empty cell. In this
# case, change the reference or enter a value other than zero.
# Raises Python ZeroDevisionError
class SSZeroDivisionError(SSError):
    ErrStr = "#DIV/0!"

# #N/A Refers to a value that is not available, or non existing (a
# blank cell for instance)

class SSNotAvailable(SSError):
    ErrStr = "#N/A"
    errDesc = "not available"

class SSAuth(SSError):
    ErrStr = "#AUTH!"
    errDesc = "Unauthorized"

# #NAME?  Uses a name that EXCEL does not recognize.
# Used for parse errors
class SSNameError(SSError):
    ErrStr = "#NAME?"

class SSRangeError(SSNameError):
    pass

# #VALUE! Uses an incorrect argument or operant.
# Raises Python ValueError

class SSValueError(SSError):
    ErrStr = "#VALUE!"

class BadArgumentsError(SSValueError):
    errDesc = "one or more invalid arguments"
    
    def __init__(self):
        ValueError.__init__(self,'bad arguments')

class WrongNumArgumentsError(SSValueError):

    def __init__(self,funcname):
        ValueError.__init__(self,'wrong number of arguments for %s' % funcname)


# #NULL!  Specifies an invalid intersection of two areas.

# #NUM!  Uses a number incorrectly for instant in the argument of a
# function. It is also displayed if the numbers are too big or too
# small to be understood by EXCEL.

class SSNumError(SSError):
    ErrStr = "#NUM!"
    errDesc = "number error"


class SSOutOfRangeError(SSNumError):
    def __init__(self):
        ValueError.__init__(self,'value out of range')

# #REF!   Refers to a cell that is not valid (non existing cell for instance).
class SSRefError(SSError):
    ErrStr = "#REF!"

    impliesFormatting = False
    def getImpliedFormatting(self,stackvalue):
        """
        getImpliedFormatting is intended for extracting formatting
        from the AST tree.  however, in some instances the ast is only
        an exception. in that case this method exists to indicate
        no formatting.
        """
        return None

    def walk(self):
        yield self

    def translate(self,dc,dr):
        return self

    def mutate(self, tR,nR,tC,nC):
        return self

class SSCircularRefError(SSRefError):
    errDesc = "circular reference"


# yummy dict
errs = dict([(x.ErrStr, x) for x in (SSZeroDivisionError, SSNameError, SSValueError, SSRefError,SSNumError)])

from twisted.web import http # for error codes

## account exceptions
class AccountExists(Exception):
    """ An account with the specified user name already exists """
    def __init__(self,userID):
        self.userID = userID
    def __str__(self):
        return '%s already exists' % (self.userID)


class AccountTokenNotExist(Exception):
    """ the account does not exist for the given verification token"""

class AccountAuthFailure(Exception):
    """ The security principal does not have access to the requested resource """
    def __init__(self,principal,objectID):
        self.objectID = objectID
        self.p = principal

    def __str__(self):
        return '%s does not have access to %d' % (str(self.p),self.objectID)


class PasswordChangeTokenExpire(Exception):
    """ the change password token has expired or is not valid """

class SelfInviteException(Exception):
    """ the user attempted to invite themself to their own sheet """

class DuplicateInviteException(Exception):
    """ the user attempted to invite an existing user """


class AccountNotVerified(Exception):
    """ the account is not verified yet """


##
## web services exceptions
##

class AccessDenied(Exception):
    """Access denied to the requested sheet"""
    httpcode = http.FORBIDDEN
    code = 4001

    def __init__(self,res):
        self.message = self.__doc__        
        self.res = res    
    def __str__(self):
        return 'access denied'

class AuthRequired(Exception):
    """attempt access a private sheet without authentication headers"""
    httpcode = http.UNAUTHORIZED
    code = 4002

    def __init__(self,res):
        self.message = self.__doc__
        self.res = res
    
    def __str__(self):
        return 'authentication required'

class InvalidSignature(Exception):
    """Invalid authorization signature"""
    httpcode = http.UNAUTHORIZED
    code = 4003
    
    def __init__(self,recv_hash,computed_hash):
        self.message = self.__doc__
        self.hash1 = recv_hash
        self.hash2 = computed_hash
    
    def __str__(self):
        return 'received %s: computed %s' % (self.hash1,self.hash2)


class AccountNotFound(Exception):
    """An account was not found for the given user id"""
    httpcode = http.UNAUTHORIZED
    code = 4004

    def __init__(self,userID):
        self.userID = userID
        self.message = self.__doc__
        
    def __str__(self):
        return 'account for %s not found' % (self.userID)


class DeleteSheetException(Exception):
    """ not possible to delete a sheet via the web service API """
    httpcode = http.FORBIDDEN
    code = 4006

    def __init__(self):
        self.message = self.__doc__

    def __str__(self):
        return 'Cannot delete entire sheet via API'

class SheetNotFound(Exception):
    """ Sheet not found """
    httpcode = http.NOT_FOUND
    code = 4007

#
# parse exceptions
#

class ParseException(Exception):
    """The XML request is malformed"""
    httpcode = http.BAD_REQUEST
    code = 4005

    def __init__(self,res):
        self.message = self.__doc__
        self.res = res

    def __str__(self):
        return 'xml parse error'

class GeneralWebSvcException(Exception):
    """The server encountered an internal error"""

    httpcode = http.INTERNAL_SERVER_ERROR
    code = 5000
    def __init__(self):
        self.message = self.__doc__
        self.res = 'unknown'

    def __str__(self):
        return 'internal server error'


#
# Literal Exceptions
#

class LiteralConversionException(Exception):
    """
    This error is throw whenever the literal has been parsed
    but the data is out of range for some reason.  If this error
    is caught the raw value should be used and no conversion is performed.
    """

#
# Database
#

class ExpansionOverflow(Exception):
    """
    the user attempted to add a number of cells or rows that would expand the sheet
    past the maximum size.
    """

#
# lock exceptiosn
#

class LockRegionOverlap(Exception):
    """
    
    """
    def __init__(self,*args):
        newargs = ('Request region overlaps with an existing locked region',) + args
        Exception.__init__(self,*newargs)

class LockRegionError(Exception):
    """
    generic error if an error occurs while attempting to change a lock.
    """
    def __init__(self):
        Exception.__init__(self,'An error occurred attempting to change a lock region')

#
# Remote web service exceptions
#

class RemoteWsTxnNotFound(Exception):
    """ The transaction was not found """

class RemoteWsTxnExpired(Exception):
    """ the transaction has expired. """

class RemoteWsTxnCancelled(Exception):
    """ the remote transaction was cancelled """

class wsNotEnoughArguments(Exception):
    def __init__(self):
        Exception.__init__(self,'not enough arguments were supplied')


class wsServiceNotFound(Exception):
    """ the service was not found """
    def __init__(self,name):
        #super(wsServiceNotFound,self).__init__('service %s not found' % name)
        Exception.__init__(self,'service %s not found' % name)


# misc

class MissingFormulaHint(ValueError):

    def __init__(self,className):
        ValueError.__init__(self,'%s does not have hint information' % className)

class MissingDocString(ValueError):
    def __init__(self,className):
        ValueError.__init__(self,'%s does not have contain a doc string' % className)


