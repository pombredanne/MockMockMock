import unittest

from MockMockMock import Mock, MockException

class TestException( Exception ):
    pass

class SingleExpectationTestCase( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock()

    def testCall( self ):
        self.mock.expect.foobar()
        self.mock.object.foobar()

    def testCallWithSimpleArgument( self ):
        self.mock.expect.foobar( 42 )
        self.mock.object.foobar( 42 )

    def testCallWithReturn( self ):
        self.mock.expect.foobar().andReturn( 42 )
        self.assertEqual( self.mock.object.foobar(), 42 )

    def testPropertyWithReturn( self ):
        self.mock.expect.foobar.andReturn( 42 )
        self.assertEqual( self.mock.object.foobar, 42 )

    def testCallWithRaise( self ):
        self.mock.expect.foobar().andRaise( TestException() )
        self.assertRaises( TestException, lambda : self.mock.object.foobar() )

    def testPropertyWithRaise( self ):
        self.mock.expect.foobar.andRaise( TestException() )
        self.assertRaises( TestException, lambda : self.mock.object.foobar )

    def testCallWithSpecificAction( self ):
        self.check = False
        def f():
            self.check = True
        self.mock.expect.foobar().andExecute( f )
        self.mock.object.foobar()
        self.assertTrue( self.check )

    def testPropertyWithSpecificAction( self ):
        self.check = False
        def f():
            self.check = True
        self.mock.expect.foobar.andExecute( f )
        self.mock.object.foobar
        self.assertTrue( self.check )

    def testCallWithBadArgument( self ):
        self.mock.expect.foobar( 42 )
        self.assertRaises( MockException, lambda : self.mock.object.foobar( 43 ) )

    def testCallWithBadName( self ):
        self.mock.expect.foobar()
        self.assertRaises( MockException, lambda : self.mock.object.barbaz() )

    def testPropertyWithBadName( self ):
        self.mock.expect.foobar.andReturn( 42 )
        self.assertRaises( MockException, lambda : self.mock.object.barbaz )

    def tearDown( self ):
        unittest.TestCase.tearDown( self )
        self.mock.tearDown()

# Expect repetitions of calls
# Expect group of calls in specific order
# Expect group of calls in any order
# Expect facultative calls
# Alternate expectations and calls
# Check that expected properties do not allow calls and vice versa
# Make the Mock.object itself callable and expect this call

unittest.main()
