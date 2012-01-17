import unittest

import MockMockMock

class TestException( Exception ):
    pass

class OneCallTestCase( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = MockMockMock.Mock()

    def testSimpleCall( self ):
        self.mock.expect.foobar()
        self.mock.object.foobar()

    def testCallWithSimpleArgument( self ):
        self.mock.expect.foobar( 42 )
        self.mock.object.foobar( 42 )

    def testCallWithReturn( self ):
        self.mock.expect.foobar().andReturn( 42 )
        self.assertEqual( self.mock.object.foobar(), 42 )

    def testCallWithRaise( self ):
        self.mock.expect.foobar().andRaise( TestException() )
        self.assertRaises( TestException, lambda : self.mock.object.foobar() )

    def testCallWithBadArgument( self ):
        self.mock.expect.foobar( 42 )
        self.assertRaises( MockMockMock.MockException, lambda : self.mock.object.foobar( 43 ) )

    def testCallWithBadName( self ):
        self.mock.expect.foobar()
        self.assertRaises( MockMockMock.MockException, lambda : self.mock.object.barbaz() )

    def tearDown( self ):
        unittest.TestCase.tearDown( self )
        self.mock.tearDown()

unittest.main()
