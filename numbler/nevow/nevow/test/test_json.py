# Copyright (c) 2004 Divmod.
# See LICENSE for details.

from twisted.trial import unittest

from nevow import json

TEST_OBJECTS = [
    0,
    None,
    True,
    False,
    [],
    [0],
    [0, 1, 2],
    [None, 1, 2],
    [None, u'one', 2],
    [True, False, u'string', 10],
    [[1, 2], [3, 4]],
    [[1.5, 2.5], [3.5, 4.5]],
    [0, [1, 2], [u'hello'], [u'world'], [True, None, False]],
    {},
    {u'foo': u'bar'},
    {u'foo': None},
    {u'bar': True},
    {u'baz': [1, 2, 3]},
    {u'quux': {u'bar': u'foo'}},
    set([1,2,3,u'foo',u'bar']),
    set(),
    [set([1,2,3]),set([u'foo',u'bar']),set([True,False,True])]
    ]

TEST_STRINGLIKE_OBJECTS = [
    u'',
    u'string',
    u'string with "embedded" quotes',
    u"string with 'embedded' single-quotes",
    u'string with \\"escaped embedded\\" quotes',
    u"string with \\'escaped embedded\\' single-quotes",
    u"string with backslashes\\\\",
    u"string with trailing accented vowels: \xe1\xe9\xed\xf3\xfa\xfd\xff",
    u"string with trailing control characters: \f\b\n\t\r",
    u'string with high codepoint characters: \u0111\u2222\u3333\u4444\uffff',
    u'string with very high codepoint characters: \U00011111\U00022222\U00033333\U00044444\U000fffff',
    ]


class JavascriptObjectNotationTestCase(unittest.TestCase):

    def testSerialize(self):
        for struct in TEST_OBJECTS:
            json.serialize(struct)

    def testRoundtrip(self):
        for struct in TEST_OBJECTS:
            bytes = json.serialize(struct)
            unstruct = json.parse(bytes)
            self.assertEquals(
                unstruct, struct,
                "Failed to roundtrip %r: %r (through %r)" % (
                    struct, unstruct, bytes))

    def testStringlikeRountrip(self):
        for struct in TEST_STRINGLIKE_OBJECTS:
            bytes = json.serialize(struct)
            unstruct = json.parse(bytes)
            failMsg = "Failed to roundtrip %r: %r (through %r)" % (
                    struct, unstruct, bytes)
            self.assertEquals(unstruct, struct, failMsg)
            self.assert_(isinstance(unstruct, unicode), failMsg)

    def testScientificNotation(self):
        self.assertEquals(json.parse('1e10'), 10**10)
        self.assertEquals(json.parse('1e0'), 1)


    def testHexEscapedCodepoints(self):
        self.assertEquals(
            json.parse('"\\xe1\\xe9\\xed\\xf3\\xfa\\xfd"'),
            u"\xe1\xe9\xed\xf3\xfa\xfd")

    def testEscapedControls(self):
        self.assertEquals(
            json.parse('"\\f\\b\\n\\t\\r"'),
            u"\f\b\n\t\r")
