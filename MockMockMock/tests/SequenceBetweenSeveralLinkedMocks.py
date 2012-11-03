# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock


class SequenceBetweenSeveralLinkedMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.m1 = self.mocks.create( "m1" )
        self.m2 = self.mocks.create( "m2" )

    def testShortCorrectSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.mocks.tearDown()

    def testShortInvertedSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            self.m2.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "m2.foobar called instead of m1.foobar" )
