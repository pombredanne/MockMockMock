# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock


class SingleExpectationNotCalled( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testMethodCallWithBadArgument( self ):
        self.myMock.expect.foobar( 42 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "myMock.foobar called with bad arguments" )

    def testMethodCallWithBadName( self ):
        self.myMock.expect.foobar()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz()
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar" )

    def testMethodCallWithBadName2( self ):
        self.myMock.expect.foobar2()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz()
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar2" )

    def testPropertyWithBadName( self ):
        self.myMock.expect.foobar.andReturn( 42 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar" )

    def testMethodNotCalled( self ):
        self.myMock.expect.foobar()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.mocks.tearDown()
        self.assertEqual( cm.exception.message, "myMock.foobar not called" )
        self.myMock.object.foobar()
        self.mocks.tearDown()

    def testPropertyNotCalled( self ):
        self.myMock.expect.foobar
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.mocks.tearDown()
        self.assertEqual( cm.exception.message, "myMock.foobar not called" )
        self.myMock.object.foobar
        self.mocks.tearDown()
