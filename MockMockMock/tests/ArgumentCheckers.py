# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net

import unittest

import MockMockMock
import MockMockMock._Details.ArgumentChecking


class ArgumentCheckers( unittest.TestCase ):
    def testCheckerIsUsedByCall( self ):
        # We use a myMock...
        checker = MockMockMock.Engine().create( "checker" )
        checker.expect( ( 12, ), {} ).andReturn( True )
        checker.expect( ( 13, ), {} ).andReturn( False )
    
        # ...to test a mock!
        m = MockMockMock.Engine().create( "m" )
        m.expect.foobar.withArguments( checker.object ).andReturn( 42 )
        m.expect.foobar.withArguments( checker.object ).andReturn( 43 )
        self.assertEqual( m.object.foobar( 12 ), 42 )
        with self.assertRaises( MockMockMock.Exception ) as cm:
            m.object.foobar( 13 )
        self.assertEqual( cm.exception.message, "m.foobar called with bad arguments" )

    # def testIdentityChecker( self ):
    # def testTypeChecker( self ):
    # def testRangeChecker( self ):

    def testEqualityChecker( self ):
        c = MockMockMock._Details.ArgumentChecking.Equality( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } )
        self.assertTrue( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } ) )
        self.assertFalse( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 4 } ) )
        self.assertFalse( c( ( 1, 2, 4 ), { 1: 1, 2: 2, 3: 3 } ) )
