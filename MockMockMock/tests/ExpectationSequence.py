# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock


class ExpectationSequence( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testTwoCalls( self ):
        self.myMock.expect.foobar()
        self.myMock.expect.barbaz()
        self.myMock.object.foobar()
        self.myMock.object.barbaz()
        self.mocks.tearDown()

    def testCallNotExpectedFirst( self ):
        self.myMock.expect.foobar()
        self.myMock.expect.barbaz()
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.barbaz()
        self.assertEqual( cm.exception.message, "myMock.barbaz called instead of myMock.foobar" )

    def testCallWithArgumentsNotExpectedFirst( self ):
        self.myMock.expect.foobar( 42 )
        self.myMock.expect.foobar( 43 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.myMock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "myMock.foobar called with bad arguments" )

    def testManyCalls( self ):
        self.myMock.expect.foobar( 1 )
        self.myMock.expect.foobar( 2 )
        self.myMock.expect.foobar( 3 )
        self.myMock.expect.foobar( 4 )
        self.myMock.expect.foobar( 5 )
        self.myMock.expect.foobar( 6 )
        self.myMock.object.foobar( 1 )
        self.myMock.object.foobar( 2 )
        self.myMock.object.foobar( 3 )
        self.myMock.object.foobar( 4 )
        self.myMock.object.foobar( 5 )
        self.myMock.object.foobar( 6 )
        self.mocks.tearDown()
