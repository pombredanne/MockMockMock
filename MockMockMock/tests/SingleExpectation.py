# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock


class TestException( Exception ):
    pass


class SingleExpectation( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mocks = MockMockMock.Engine()
        self.myMock = self.mocks.create( "myMock" )

    def tearDown( self ):
        self.mocks.tearDown()

    def testMethodCall( self ):
        self.myMock.expect.foobar()
        self.myMock.object.foobar()

    def testMethodCallWithSimpleArgument( self ):
        self.myMock.expect.foobar( 42 )
        self.myMock.object.foobar( 42 )

    def testMethodCallWithReturn( self ):
        returnValue = object()
        self.myMock.expect.foobar().andReturn( returnValue )
        self.assertIs( self.myMock.object.foobar(), returnValue )

    def testPropertyWithReturn( self ):
        self.myMock.expect.foobar.andReturn( 42 )
        self.assertEqual( self.myMock.object.foobar, 42 )

    def testObjectCallWithArgumentsAndReturn( self ):
        self.myMock.expect( 43, 44 ).andReturn( 42 )
        self.assertEqual( self.myMock.object( 43, 44 ), 42 )

    def testMethodCallWithRaise( self ):
        self.myMock.expect.foobar().andRaise( TestException() )
        with self.assertRaises( TestException ):
            self.myMock.object.foobar()

    def testPropertyWithRaise( self ):
        self.myMock.expect.foobar.andRaise( TestException() )
        with self.assertRaises( TestException ):
            self.myMock.object.foobar

    def testMethodCallWithSpecificAction( self ):
        self.check = False
        def f():
            self.check = True
        self.myMock.expect.foobar().andExecute( f )
        self.myMock.object.foobar()
        self.assertTrue( self.check )

    def testPropertyWithSpecificAction( self ):
        self.check = False
        def f():
            self.check = True
        self.myMock.expect.foobar.andExecute( f )
        self.myMock.object.foobar
        self.assertTrue( self.check )
