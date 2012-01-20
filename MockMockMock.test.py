import unittest
from operator import isCallable # deprecated, but documented alternative requires __mro__ to be defined in callable class

from MockMockMock import Mock, MockException

class TestException( Exception ):
    pass

class PublicInterface( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def testMock( self ):
        self.assertEqual( self.dir( self.mock ), [ "expect", "object", "tearDown" ] )
        self.assertFalse( isCallable( self.mock ) )

    def testExpect( self ):
        self.assertEqual( self.dir( self.mock.expect ), [] )
        self.assertTrue( isCallable( self.mock.expect ) )

    def testExpectation( self ):
        self.assertEqual( self.dir( self.mock.expect.foobar ), [ "andExecute", "andRaise", "andReturn", "withArguments" ] )
        self.assertTrue( isCallable( self.mock.expect.foobar ) )

    def testCalledExpectation( self ):
        self.assertEqual( self.dir( self.mock.expect.foobar( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.mock.expect.foobar( 42 ) ) )
        self.assertEqual( self.dir( self.mock.expect.foobar.withArguments( 42 ) ), [ "andExecute", "andRaise", "andReturn" ] )
        self.assertFalse( isCallable( self.mock.expect.foobar.withArguments( 42 ) ) )

    def testCalledThenAndedExpectation( self ):
        self.assertEqual( self.dir( self.mock.expect.foobar( 42 ).andReturn( 12 ) ), [] )
        self.assertFalse( isCallable( self.mock.expect.foobar( 42 ).andReturn( 12 ) ) )
        self.assertEqual( self.dir( self.mock.expect.foobar( 42 ).andRaise( TestException() ) ), [] )
        self.assertFalse( isCallable( self.mock.expect.foobar( 42 ).andRaise( TestException() ) ) )
        self.assertEqual( self.dir( self.mock.expect.foobar( 42 ).andExecute( lambda : 12 ) ), [] )
        self.assertFalse( isCallable( self.mock.expect.foobar( 42 ).andExecute( lambda : 12 ) ) )

    def testAndedExpectation( self ):
        self.assertEqual( self.dir( self.mock.expect.foobar.andReturn( 12 ) ), [] )
        self.assertFalse( isCallable( self.mock.expect.foobar.andReturn( 12 ) ) )
        self.assertEqual( self.dir( self.mock.expect.foobar.andRaise( TestException() ) ), [] )
        self.assertFalse( isCallable( self.mock.expect.foobar.andRaise( TestException() ) ) )
        self.assertEqual( self.dir( self.mock.expect.foobar.andExecute( lambda : 12 ) ), [] )
        self.assertFalse( isCallable( self.mock.expect.foobar.andExecute( lambda : 12 ) ) )

    def testObject( self ):
        self.assertEqual( self.dir( self.mock.object ), [] )

    def dir( self, o ):
        return sorted( a for a in dir( o ) if not a.startswith( "_" ) )

class SingleExpectation( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

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
        with self.assertRaises( TestException ):
            self.mock.object.foobar()

    def testPropertyWithRaise( self ):
        self.mock.expect.foobar.andRaise( TestException() )
        with self.assertRaises( TestException ):
            self.mock.object.foobar

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
        with self.assertRaises( MockException ) as cm:
            self.mock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "MyMock.foobar called with bad arguments" )

    def testCallWithBadName( self ):
        self.mock.expect.foobar()
        with self.assertRaises( MockException ) as cm:
            self.mock.object.barbaz()
        self.assertEqual( cm.exception.message, "MyMock.barbaz called instead of MyMock.foobar" )

    def testPropertyWithBadName( self ):
        self.mock.expect.foobar.andReturn( 42 )
        with self.assertRaises( MockException ) as cm:
            self.mock.object.barbaz
        self.assertEqual( cm.exception.message, "MyMock.barbaz called instead of MyMock.foobar" )

    def testTearDown( self ):
        self.mock.expect.foobar
        with self.assertRaises( MockException ) as cm:
            self.mock.tearDown()
        self.assertEqual( cm.exception.message, "MyMock.foobar not called" )
        self.mock.object.foobar
        self.mock.tearDown()

class ExpectationSequence( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def testTwoCalls( self ):
        self.mock.expect.foobar()
        self.mock.expect.barbaz()
        self.mock.object.foobar()
        self.mock.object.barbaz()
        self.mock.tearDown()

    def testCallNotExpectedFirst( self ):
        self.mock.expect.foobar()
        self.mock.expect.barbaz()
        with self.assertRaises( MockException):
            self.mock.object.barbaz()

    def testCallWithArgumentsNotExpectedFirst( self ):
        self.mock.expect.foobar( 42 )
        self.mock.expect.foobar( 43 )
        with self.assertRaises( MockException ) as cm:
            self.mock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "MyMock.foobar called with bad arguments" )

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
        self.mock.tearDown()

    # def testRepeatedCall( self ):
        # self.mock.expect.foobar( 42 ).andReturn( 53 ).repeated( 3 )
        # for i in range( 3 ):
            # self.assertEqual( self.mock.object.foobar( 42 ), 53 )

class SequenceBetweenSeveralLinkedMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.m1 = Mock( "m1" )
        self.m2 = Mock( "m2", self.m1 )
        self.m3 = Mock( "m3", self.m1 )

    def testShortCorrectSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.barbaz( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.barbaz( 43 )
        self.m1.tearDown()

    def testShortInvertedSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.barbaz( 43 )
        with self.assertRaises( MockException ) as cm:
            self.m2.object.barbaz( 43 )

class SequenceBetweenSeveralIndependentMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.m1 = Mock( "m1" )
        self.m2 = Mock( "m2" )

    def testSameOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.barbaz( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.barbaz( 43 )
        self.m1.tearDown()
        self.m2.tearDown()

    def testOtherOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.barbaz( 43 )
        self.m2.object.barbaz( 43 )
        self.m1.object.foobar( 42 )
        self.m1.tearDown()
        self.m2.tearDown()

class ExpectationAndCallAlternation( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def test( self ):
        self.mock.expect.foobar( 42 )
        self.mock.expect.foobar( 43 )
        self.mock.object.foobar( 42 )
        self.mock.expect.foobar( 44 )
        self.mock.object.foobar( 43 )
        self.mock.object.foobar( 44 )
        self.mock.tearDown()

# Expect repetitions of calls
# Expect group of calls in specific order
# Expect group of calls in any order
# Expect facultative calls
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
