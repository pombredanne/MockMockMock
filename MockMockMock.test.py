import unittest
from operator import isCallable # deprecated, but documented alternative requires __mro__ to be defined in callable class

from MockMockMock import Mock, MockException

class TestException( Exception ):
    pass

class PublicInterface( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock()

    def testMock( self ):
        self.assertEqual( self.dir( self.mock ), [ "expect", "object", "tearDown" ] )

    def testExpect( self ):
        self.assertEqual( self.dir( self.mock.expect ), [] )

    def testExpectation( self ):
        self.assertEqual( self.dir( self.mock.expect.foobar ), [ "andExecute", "andRaise", "andReturn", "withArguments" ] )
        self.assertTrue( isCallable( self.mock.expect.foobar ) )

    def testCalledExpectation( self ):
        self.assertEqual( self.dir( self.mock.expect.foobar( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.mock.expect.foobar( 42 ) ) )
        self.assertEqual( self.dir( self.mock.expect.foobar.withArguments( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.mock.expect.foobar.withArguments( 42 ) ) )

    def testAndedExpectation( self ):
        self.assertEqual( self.dir( self.mock.expect.foobar.withArguments( 42 ).andReturn( 12 ) ), [] )
        self.assertEqual( self.dir( self.mock.expect.foobar.withArguments( 42 ).andRaise( TestException() ) ), [] )
        self.assertEqual( self.dir( self.mock.expect.foobar.withArguments( 42 ).andExecute( lambda : 12 ) ), [] )

    def testObject( self ):
        self.assertEqual( self.dir( self.mock.object ), [] )

    def dir( self, o ):
        return sorted( a for a in dir( o ) if not a.startswith( "_" ) )

class SingleExpectation( unittest.TestCase ):
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

    def testTearDown( self ):
        self.mock.expect.foobar
        self.assertRaises( MockException, self.mock.tearDown )
        self.mock.object.foobar
        self.mock.tearDown()

class ExpectationSequence( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock()

    def testTwoCalls( self ):
        self.mock.expect.foobar()
        self.mock.expect.barbaz()
        self.mock.object.foobar()
        self.mock.object.barbaz()

    def testCallNotExpectedFirst( self ):
        self.mock.expect.foobar()
        self.mock.expect.barbaz()
        self.assertRaises( MockException, lambda : self.mock.object.barbaz() )

    def testCallWithArgumentsNotExpectedFirst( self ):
        self.mock.expect.foobar( 42 )
        self.mock.expect.foobar( 43 )
        self.assertRaises( MockException, lambda : self.mock.object.foobar( 43 ) )

    def testManyCalls( self ):
        self.mock.expect.foo_1()
        self.mock.expect.foo_2()
        self.mock.expect.foo_3()
        self.mock.expect.foo_4()
        self.mock.expect.foo_5()
        self.mock.expect.foo_6()
        self.mock.object.foo_1()
        self.mock.object.foo_2()
        self.mock.object.foo_3()
        self.mock.object.foo_4()
        self.mock.object.foo_5()
        self.mock.object.foo_6()

    # def testRepeatedCall( self ):
        # self.mock.expect.foobar( 42 ).andReturn( 53 ).repeated( 3 )
        # for i in range( 3 ):
            # self.assertEqual( self.mock.object.foobar( 42 ), 53 )

# Expect repetitions of calls
# Expect group of calls in specific order
# Expect group of calls in any order
# Expect facultative calls
# Alternate expectations and calls
# Check that expected properties do not allow calls and vice versa
# Make the Mock.object itself callable and expect this call
# Check that forgeting the last call raises a MockException in Mock.tearDown
# Allow other arguments checking than simple constants
# Maybe mock.expect.foobar.withArguments( 42 ) could be a synonym for mock.expect.foobar( 42 ) and we could add a withArgumentsChecker to handle more complex cases
# Transmit arguments to andExecute's callable (usefull when repeated): mock.expect.foobar( 12 ).andExecute( lambda n : n + 1 ).repeated( 5 )
# Check that unordered property and method calls on the same name can happen
# Derive a class from unittest.TestCase that provides a mock factory and auto-tearDowns the created mocks
# Manage expectations from several Mocks: they shall be ordered globaly or on a given Mock collection

unittest.main()
