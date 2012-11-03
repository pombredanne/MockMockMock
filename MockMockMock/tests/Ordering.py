# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock


class Ordering( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testUnorderedGroupOfSameMethod( self ):
        with self.mocks.unordered:
            self.myMock.expect.foobar( 1 ).andReturn( 11 )
            self.myMock.expect.foobar( 1 ).andReturn( 13 )
            self.myMock.expect.foobar( 2 ).andReturn( 12 )
            self.myMock.expect.foobar( 1 ).andReturn( 14 )
        self.assertEqual( self.myMock.object.foobar( 2 ), 12 )
        self.assertEqual( self.myMock.object.foobar( 1 ), 11 )
        self.assertEqual( self.myMock.object.foobar( 1 ), 13 )
        self.assertEqual( self.myMock.object.foobar( 1 ), 14 )
        self.mocks.tearDown()

    ### @todo Allow unordered property and method calls on the same name: difficult
    def testUnorderedGroupOfSameMethodAndProperty( self ):
        with self.assertRaises( MockMockMock.Exception ) as cm:
            with self.mocks.unordered:
                self.myMock.expect.foobar()
                self.myMock.expect.foobar
            self.myMock.object.foobar
        self.assertEqual( cm.exception.message, "myMock.foobar is expected as a property and as a method call in an unordered group" )

    def testUnorderedGroupOfSamePropertyAndMethod( self ):
        with self.assertRaises( MockMockMock.Exception ) as cm:
            with self.mocks.unordered:
                self.myMock.expect.foobar
                self.myMock.expect.foobar()
            self.myMock.object.foobar()
        self.assertEqual( cm.exception.message, "myMock.foobar is expected as a property and as a method call in an unordered group" )
