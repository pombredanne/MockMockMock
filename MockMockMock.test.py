import unittest
from operator import isCallable # deprecated, but documented alternative requires __mro__ to be defined in callable class

from MockMockMock import Mock, MockException
import MockMockMock.ArgumentCheckers as Checkers

class TestException( Exception ):
    pass

class PublicInterface( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def testMock( self ):
        self.assertEqual( self.dir( self.mock ), [ "expect", "object", "ordered", "tearDown", "unordered" ] )
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

    def testMethodCall( self ):
        self.mock.expect.foobar()
        self.mock.object.foobar()

    def testMethodCallWithSimpleArgument( self ):
        self.mock.expect.foobar( 42 )
        self.mock.object.foobar( 42 )

    def testMethodCallWithReturn( self ):
        returnValue = object()
        self.mock.expect.foobar().andReturn( returnValue )
        self.assertTrue( self.mock.object.foobar() is returnValue )

    def testPropertyWithReturn( self ):
        self.mock.expect.foobar.andReturn( 42 )
        self.assertEqual( self.mock.object.foobar, 42 )

    def testObjectCallWithArgumentsAndReturn( self ):
        self.mock.expect( 43, 44 ).andReturn( 42 )
        self.assertEqual( self.mock.object( 43, 44 ), 42 )

    def testMethodCallWithRaise( self ):
        self.mock.expect.foobar().andRaise( TestException() )
        with self.assertRaises( TestException ):
            self.mock.object.foobar()

    def testPropertyWithRaise( self ):
        self.mock.expect.foobar.andRaise( TestException() )
        with self.assertRaises( TestException ):
            self.mock.object.foobar

    def testMethodCallWithSpecificAction( self ):
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

    def testMethodCallWithBadArgument( self ):
        self.mock.expect.foobar( 42 )
        with self.assertRaises( MockException ) as cm:
            self.mock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "MyMock.foobar called with bad arguments" )

    def testMethodCallWithBadName( self ):
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

class ArgumentCheckers( unittest.TestCase ):
    # def testIdentityChecker( self ):

    def testEqualityChecker( self ):
        c = Checkers.Equality( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } )
        self.assertTrue( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } ) )
        self.assertFalse( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 4 } ) )
        self.assertFalse( c( ( 1, 2, 4 ), { 1: 1, 2: 2, 3: 3 } ) )
    
    # def testTypeChecker( self ):
    
    # def testRangeChecker( self ):

    def testCheckerIsUsedByCall( self ):
        # We use a mock...
        checker = Mock( "checker" )
        checker.expect( ( 12, ), {} ).andReturn( True )
        checker.expect( ( 13, ), {} ).andReturn( False )
    
        # ...to test a mock!
        m = Mock( "m" )
        m.expect.foobar.withArguments( checker.object ).andReturn( 42 )
        m.expect.foobar.withArguments( checker.object ).andReturn( 43 )
        self.assertEqual( m.object.foobar( 12 ), 42 )
        with self.assertRaises( MockException ) as cm:
            m.object.foobar( 13 )
        self.assertEqual( cm.exception.message, "m.foobar called with bad arguments" )

class Ordering( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def testUnorderedGroup( self ):
        with self.mock.unordered:
            self.mock.expect.foobar().andReturn( 1 )
            self.mock.expect.barbaz().andReturn( 2 )
        self.assertEqual( self.mock.object.barbaz(), 2 )
        self.assertEqual( self.mock.object.foobar(), 1 )
        self.mock.tearDown()

    def testUnorderedGroupOfSameMethod( self ):
        with self.mock.unordered:
            self.mock.expect.foobar( 1 ).andReturn( 11 )
            self.mock.expect.foobar( 1 ).andReturn( 13 )
            self.mock.expect.foobar( 2 ).andReturn( 12 )
            self.mock.expect.foobar( 1 ).andReturn( 14 )
        self.assertEqual( self.mock.object.foobar( 2 ), 12 )
        self.assertEqual( self.mock.object.foobar( 1 ), 11 )
        self.assertEqual( self.mock.object.foobar( 1 ), 13 )
        self.assertEqual( self.mock.object.foobar( 1 ), 14 )
        self.mock.tearDown()

    def testUnorderedGroupOfSamePropertyAndAnother( self ):
        with self.mock.unordered:
            self.mock.expect.foobar.andReturn( 11 )
            self.mock.expect.barbaz.andReturn( 12 )
            self.mock.expect.foobar.andReturn( 13 )
            self.mock.expect.barbaz.andReturn( 14 )
        self.assertEqual( self.mock.object.barbaz, 12 )
        self.assertEqual( self.mock.object.foobar, 11 )
        self.assertEqual( self.mock.object.barbaz, 14 )
        self.assertEqual( self.mock.object.foobar, 13 )
        self.mock.tearDown()

    def testUnorderedGroupOfSameMethodAndAnother( self ):
        with self.mock.unordered:
            self.mock.expect.foobar( 1 )
            self.mock.expect.foobar( 2 )
            self.mock.expect.barbaz()
        self.mock.object.foobar( 2 )
        self.mock.object.barbaz()
        self.mock.object.foobar( 1 )
        self.mock.tearDown()

    def testUnorderedGroupOfSameMethodAndProperty( self ):
        with self.assertRaises( MockException ) as cm:
            with self.mock.unordered:
                self.mock.expect.foobar()
                self.mock.expect.foobar
            self.mock.object.foobar
            self.mock.object.foobar()
        self.assertEqual( cm.exception.message, "MyMock.foobar is expected as a property and as a method call in an unordered group" )

    def testUnorderedGroupOfSamePropertyAndMethod( self ):
        with self.assertRaises( MockException ) as cm:
            with self.mock.unordered:
                self.mock.expect.foobar
                self.mock.expect.foobar()
            self.mock.object.foobar()
            self.mock.object.foobar
        self.assertEqual( cm.exception.message, "MyMock.foobar is expected as a property and as a method call in an unordered group" )

class OrderedGroupInUnordered( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )
        with self.mock.unordered:
            self.mock.expect.u1()
            with self.mock.ordered:
                self.mock.expect.u2o1()
                self.mock.expect.u2o2()
                self.mock.expect.u2o3()
            self.mock.expect.u3()

    def testOriginalOrder( self ):
        self.mock.object.u1()
        self.mock.object.u2o1()
        self.mock.object.u2o2()
        self.mock.object.u2o3()
        self.mock.object.u3()
        self.mock.tearDown()

# Expect group of calls in any order
# Expect group of calls in specific order
# Expect facultative calls
# Expect repetitions of calls
# Test groups in groups in groups in...

# Allow other arguments checking than simple constants
# Maybe mock.expect.foobar.withArguments( 42 ) could be a synonym for mock.expect.foobar( 42 ) and we could add a withArgumentsChecker to handle more complex cases
# Transmit arguments to andExecute's callable (usefull when repeated, or with other arguments checkers): mock.expect.foobar( 12 ).andExecute( lambda n : n + 1 ).repeated( 5 )
# Allow positional arguments (*args) to be passed by name (**kwds)

# Check that expected properties do not allow calls and vice versa
# Check that unordered method calls on the same name with different arguments can happen
# Check that unordered property and method calls on the same name can happen

# Derive a class from unittest.TestCase that provides a mock factory and auto-tearDowns the created mocks

unittest.main()
