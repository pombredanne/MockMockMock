# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest
import collections

import MockMockMock

def isCallable( x ):
    return isinstance( x, collections.Callable )

class TestException( Exception ):
    pass

class PublicInterface( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def testMockMockMock( self ):
        self.assertEqual( self.dir( MockMockMock ), [ "Engine", "Exception", "tests" ] )

    def testEngine( self ):
        self.assertEqual( self.dir( self.mocks ), [ "alternative", "atomic", "create", "optional", "ordered", "repeated", "tearDown", "unordered" ] )
        self.assertFalse( isCallable( self.mocks ) )

    def testMock( self ):
        self.assertEqual( self.dir( self.myMock ), [ "expect", "object" ] )
        self.assertFalse( isCallable( self.myMock ) )

    def testExpect( self ):
        self.assertEqual( self.dir( self.myMock.expect ), [] )
        self.assertTrue( isCallable( self.myMock.expect ) )

    def testExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar ), [ "andExecute", "andRaise", "andReturn", "withArguments" ] )
        self.assertTrue( isCallable( self.myMock.expect.foobar ) )

    def testCalledExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar.withArguments( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.withArguments( 42 ) ) )

    def testCalledThenAndedExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ).andReturn( 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ).andReturn( 12 ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ).andRaise( TestException() ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ).andRaise( TestException() ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar( 42 ).andExecute( lambda : 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar( 42 ).andExecute( lambda : 12 ) ) )

    def testAndedExpectation( self ):
        self.assertEqual( self.dir( self.myMock.expect.foobar.andReturn( 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.andReturn( 12 ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar.andRaise( TestException() ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.andRaise( TestException() ) ) )
        self.assertEqual( self.dir( self.myMock.expect.foobar.andExecute( lambda : 12 ) ), [] )
        self.assertFalse( isCallable( self.myMock.expect.foobar.andExecute( lambda : 12 ) ) )

    def testObject( self ):
        ### @todo Maybe expose expected calls in myMock.object.__dir__
        self.assertEqual( self.dir( self.myMock.object ), [] )

    def dir( self, o ):
        return sorted( a for a in dir( o ) if not a.startswith( "_" ) )
