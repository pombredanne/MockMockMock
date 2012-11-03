# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock


class SequenceBetweenSeveralIndependentMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks1 = MockMockMock.Engine()
        self.mocks2 = MockMockMock.Engine()
        self.m1 = self.mocks1.create( "m1" )
        self.m2 = self.mocks2.create( "m2" )

    def testSameOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.mocks1.tearDown()
        self.mocks2.tearDown()

    def testOtherOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m2.object.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.mocks1.tearDown()
        self.mocks2.tearDown()
