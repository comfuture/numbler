#!/usr/bin/env python

from numbler.unittests.testtools import *


class formulaLiteralTestCase(formulaTestCase):
    """ test case for literals that are prefixed by a =.  In most cases
    this simply duplicates the other tests with a couple of specific examples,
    most notabily the difference between ints and longs.
    """

    def testLongLits(self):

        val = self.getParsed("1000000000000000")
        self.failUnless(val.eval(1) == 1000000000000000)



class literalTestCase(formulaTestCase):
    """ test basic formulas that don't require a persisted sheet"""

    def testNegative(self):
        val = self.parseLiteralNumber('-55');
        self.failUnless(val == -55);
        val = self.parseLiteralNumber('---55');
        # this returns a string right now
        #self.failUnless(val == -55);        

    def positive(self):
        val = self.parseLiteralNumber('+0');
        self.failUnless(val == 0);
        val = self.parseLiteralNumber('+0.0001');
        self.failUnless(val == 0.0001);
        val = self.parseLiteralNumber('$+3.45');
        self.failUnless(val == 3.45);                



    def testCurrency(self):
        val = self.parseLiteralNumber('$345.29');
        self.failUnless(val == 345.29);
        val = self.parseLiteralNumber('$1,000,000');
        self.failUnless(val == 1000000);

        val = self.parseLiteralNumber('$.334');
        self.failUnless(val == 0.334);                

    def testPercentage(self):
        val = self.parseLiteralNumber('1000%');
        self.failUnless(val == 10);
        val = self.parseLiteralNumber('100%');
        self.failUnless(val == 1);
        val = self.parseLiteralNumber('+5%');
        self.failUnless(val == 0.05);
        val = self.parseLiteralNumber('-5%');
        self.failUnless(val == -0.05);
        val = self.parseLiteralNumber('50%%');
        self.failUnless(val == '50%%');
        val = self.parseLiteralNumber('3.5%');
        self.failUnless(val == 0.035);
        val = self.parseLiteralNumber('.5%');
        self.failUnless(val == 0.005);                


    def testFractions(self):
        val = self.parseLiteralNumber('52.');
        self.failUnless(val == 52.0);
        val = self.parseLiteralNumber('.');
        self.failUnless(val == '.');
        val = self.parseLiteralNumber('.9e5');
        self.failUnless(val == 90000.0);                        

        
    def testScientificNotation(self):
        val = self.parseLiteralNumber('1.2e5');
        self.failUnless(val == 120000);
        val = self.parseLiteralNumber('-1.2e5');
        self.failUnless(val == -120000);
        val = self.parseLiteralNumber('-120000e-2');
        self.failUnless(val == -1200);
        val = self.parseLiteralNumber('2e-4');
        self.failUnless(self.roundedResult(val) == "0.0002");
        val = self.parseLiteralNumber('-2e-4');
        self.failUnless(self.roundedResult(val) == "-0.0002");                                                

    def testLeadingSpaces(self):
        val = self.parseLiteralNumber('   $3   ');
        self.failUnless(val == 3);

        val = self.parseLiteralNumber('   $3.5   ');
        self.failUnless(val == 3.5);        

        val = self.parseLiteralNumber('   3%');
        self.failUnless(val == 0.03);

        val = self.parseLiteralNumber('   3        %');
        self.failUnless(val == 0.03);

        val = self.parseLiteralNumber('   3.4        %');
        self.failUnless(val == 0.034);                

        val = self.parseLiteralNumber('3.4         %');
        self.failUnless(val == 0.034);

        val = self.parseLiteralNumber('  -  3.4         %');
        self.failUnless(val == -0.034);

        val = self.parseLiteralNumber('  +  .4         %');
        self.failUnless(val == 0.004);                                        

        val = self.parseLiteralNumber('   ');
        self.failUnless(val == '   ');

        val = self.parseLiteralNumber(' $3.0004  ');
        self.failUnless(val == 3.0004);

        val = self.parseLiteralNumber('$       3.0004');
        self.failUnless(val == 3.0004);

        val = self.parseLiteralNumber('$       3.0004         $');
        self.failUnless(val == '$       3.0004         $');

        val = self.parseLiteralNumber('   3.5e -2');
        self.failUnless(val == '   3.5e -2');                


class literalTimeTestCase(formulaTestCase):

    def testShortTime(self):

        val = self.parseLiteralNumber('5 p')
        self.failUnless(self.roundedResult(val) == '0.7083')
        val = self.parseLiteralNumber('5 pm')
        self.failUnless(self.roundedResult(val) == '0.7083')
        val = self.parseLiteralNumber('5 Pm')
        self.failUnless(self.roundedResult(val) == '0.7083')
        val = self.parseLiteralNumber('5 PM')
        self.failUnless(self.roundedResult(val) == '0.7083')                        
        val = self.parseLiteralNumber('5 am')
        self.failUnless(self.roundedResult(val) == '0.2083')                                
        val = self.parseLiteralNumber('5 a')        
        self.failUnless(self.roundedResult(val) == '0.2083')        

        # negative tests
        val = self.parseLiteralNumber('13 a')        
        self.failUnless(val == '13 a')
        val = self.parseLiteralNumber('13 am')        
        self.failUnless(val == '13 am')
        val = self.parseLiteralNumber('23 am')        
        self.failUnless(val == '23 am')
        val = self.parseLiteralNumber('25 p')                
        self.failUnless(val == '25 p')                                

    def testMedTime(self):

        val = self.parseLiteralNumber('11:13')
        self.failUnless(self.roundedResult(val) == '0.4674')
        val = self.parseLiteralNumber('11:13 p')
        self.failUnless(self.roundedResult(val) == '0.9674')
        val = self.parseLiteralNumber('14:59')
        self.failUnless(self.roundedResult(val) == '0.6243')                
        val = self.parseLiteralNumber('00:00 p')
        self.failUnless(val == 0.5)                                        
        val = self.parseLiteralNumber('0:0 p')
        self.failUnless(val == 0.5)
        val = self.parseLiteralNumber('12:30 a')
        self.failUnless(self.roundedResult(val) == '0.0208')                        

        val = self.parseLiteralNumber('0:0')
        self.failUnless(val == 0)
        val = self.parseLiteralNumber('00:0')
        self.failUnless(val == 0)                                                                
        val = self.parseLiteralNumber('00:0 a')
        self.failUnless(val == 0)
        val = self.parseLiteralNumber('23:59')
        self.failUnless(self.roundedResult(val) == '0.9993')
        val = self.parseLiteralNumber('11:59 PM')
        self.failUnless(self.roundedResult(val) == '0.9993')                


        # negative tests
        val = self.parseLiteralNumber('14:61')
        self.failUnless(val == '14:61')
        val = self.parseLiteralNumber('61:03')
        self.failUnless(val == '61:03')        

    def testLongTime(self):
        val = self.parseLiteralNumber('00:00:00 a')
        self.failUnless(val == 0)        
        val = self.parseLiteralNumber('0:0:0 a')
        self.failUnless(val == 0)                
        val = self.parseLiteralNumber('0:0:0')
        self.failUnless(val == 0)                
        val = self.parseLiteralNumber('00:00:00')
        self.failUnless(val == 0)

        val = self.parseLiteralNumber('12:23:59 a')
        self.failUnless(self.roundedResult(val) == '0.0167')        
        val = self.parseLiteralNumber('11:31:57 p')
        self.failUnless(self.roundedResult(val) == '0.9805')        
        val = self.parseLiteralNumber('11:31:57 a')
        self.failUnless(self.roundedResult(val) == '0.4805')
        val = self.parseLiteralNumber('12:0:1 p')
        self.failUnless(self.roundedResult(val) == '0.5000')
        val = self.parseLiteralNumber('16:34:30 ')        
        self.failUnless(self.roundedResult(val) == '0.6906')

        # negative
        val = self.parseLiteralNumber('16:34:99 p')
        self.failUnless(val == '16:34:99 p')
        val = self.parseLiteralNumber('16:34: p')
        self.failUnless(val == '16:34: p')        



class literalDateTestCase(formulaTestCase):
    """ note: the short date tests will start to fail in 2007!!!! """

    def testShortDates(self):
        val = self.parseLiteralNumber('3-Jan')
        self.failUnless(val == 38720)    
        val = self.parseLiteralNumber('3/Jan')
        self.failUnless(val == 38720)        

        val = self.parseLiteralNumber('12/31')
        self.failUnless(val == 39082)                
        val = self.parseLiteralNumber('12-31')
        self.failUnless(val == 39082)                
        val = self.parseLiteralNumber('9/1')
        self.failUnless(val == 38961)        
        val = self.parseLiteralNumber('1-9')                        
        self.failUnless(val == 38726)

        val = self.parseLiteralNumber('Mar-2008')
        self.failUnless(val == 39508)
        val = self.parseLiteralNumber('Mar-15')
        self.failUnless(val == 38791)        
        
        
        # negative
        val = self.parseLiteralNumber('30/Feb')
        self.failUnless(val == '30/Feb')
        val = self.parseLiteralNumber('14-23')
        self.failUnless(val == '14-23')    
        val = self.parseLiteralNumber('30-2')
        self.failUnless(val == '30-2')
        val = self.parseLiteralNumber('2005-12-12')
        self.failUnless(val == '2005-12-12')        

    def testLongDates(self):
        val = self.parseLiteralNumber('Jul 3, 2005')
        self.failUnless(val == 38536)                
        val = self.parseLiteralNumber('July/3, 2005')
        self.failUnless(val == 38536)                        
        val = self.parseLiteralNumber('July 3, 2005')
        self.failUnless(val == 38536)                        

        val = self.parseLiteralNumber('11/12/2009')
        self.failUnless(val == 40129)                                
        val = self.parseLiteralNumber('01-01-2001')
        self.failUnless(val == 36892)
        val = self.parseLiteralNumber('1-1-2001')        

        # negative
        val = self.parseLiteralNumber('mar-15-2008')
        self.failUnless(val == 'mar-15-2008')


class literalDateTimeTestCase(formulaTestCase):

    def testDateTimes(self):
        val = self.parseLiteralNumber('July 3, 2005 12:23:30 p')
        self.failUnless(self.roundedResult(val) == '38536.5163')
        val = self.parseLiteralNumber('Apr 9, 2005 11 p')
        self.failUnless(self.roundedResult(val) == '38451.9583')        
        val = self.parseLiteralNumber('Apr 9, 2005 11:34')
        self.failUnless(self.roundedResult(val) == '38451.4819')        
        val = self.parseLiteralNumber('9/apr 00:1')
        self.failUnless(self.roundedResult(val) == '38816.0007')        
        val = self.parseLiteralNumber('18/oct 2:30 p')
        self.failUnless(self.roundedResult(val) == '39008.6042')        
        val = self.parseLiteralNumber('18/oct 2:30 p')
        self.failUnless(self.roundedResult(val) == '39008.6042')        



class frTestCase(formulaTestCase):
    localestr = 'fr_FR'
    
    def testDateTimes(self):
        #val = self.parseLiteralNumber('3/Juin-2005 12:23:30 p')
        #self.failUnless(self.roundedResult(val) == '38536.5163')
        val = self.parseLiteralNumber('9/avr.-2005 11 p')
        self.failUnless(self.roundedResult(val) == '38451.9583')        
        val = self.parseLiteralNumber('9/avr.-2005 11:34')
        self.failUnless(self.roundedResult(val) == '38451.4819')        
        #val = self.parseLiteralNumber('9/avr. 00:1')
        #self.failUnless(self.roundedResult(val) == '38816.0007')        
        #val = self.parseLiteralNumber('18/oct. 2:30 p')
        #self.failUnless(self.roundedResult(val) == '39008.6042')
        val = self.parseLiteralNumber('9/avr./2006 00:1')
        self.failUnless(self.roundedResult(val) == '38816.0007')        
        val = self.parseLiteralNumber('18/oct./2006 2:30 p')
        self.failUnless(self.roundedResult(val) == '39008.6042')                
        #val = self.parseLiteralNumber('18/oct./2006 2:30p')
        #self.failUnless(self.roundedResult(val) == '39008.6042')        

    def testFractions(self):
        val = self.parseLiteralNumber('52,');
        self.failUnless(val == 52.0);
        val = self.parseLiteralNumber(',');
        self.failUnless(val == ',');
        val = self.parseLiteralNumber(',9e5');
        self.failUnless(val == 90000.0);                                

    def testCurrency(self):
        val = self.parseLiteralNumber('345,29 \xe2\x82\xac')
        self.failUnless(val == 345.29)
        val = self.parseLiteralNumber('1 000 000 \xe2\x82\xac')
        self.failUnless(val == 1000000)

        val = self.parseLiteralNumber(',334 \xe2\x82\xac')
        self.failUnless(val == 0.334)               


class usStringsTestCase(formulaTestCase):
    localestr = 'en_US'

    def testNonNumericLiterals(self):
        vals = [
            '  hi.  how are you?  ',
            'hi.',
            'enter something like "3.45"',
            '.9 units',
            '.9a',
            '$$$$',
            '$',
            '%',
            ',',
            '3ee9'
            ]
        for x in vals:
            val = self.parseLiteralNumber(x)
            self.failUnless(val == x)
        
class frStringsTestCase(formulaTestCase):
    localestr = 'fr_FR'

    def testNonNumericLiterals(self):
        vals = [
            '  hi.  how are you?  ',
            'hi.',
            'enter something like "3.45"',
            '.9 units',
            '.9a',
            '3,5,4',
            '%$',
            ',moi?'
            ]
        for x in vals:
            val = self.parseLiteralNumber(x)
            self.failUnless(val == x)

    

suitelist = [literalTestCase,literalTimeTestCase,literalDateTestCase,
             literalDateTimeTestCase,
             frTestCase,
             usStringsTestCase,frStringsTestCase]


if __name__ == '__main__': testmain(suitelist)
