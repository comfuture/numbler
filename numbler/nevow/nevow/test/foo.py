#!/usr/bin/env python

from twisted.trial import unittest
import test_json

suite = unittest.makeSuite(test_json.JavascriptObjectNotationTestCase)

def main():
    t = unittest.TextTestRunner()
    t.run(suite)


if __name__ == '__main__': main()
