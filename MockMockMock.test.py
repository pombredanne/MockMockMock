import unittest
from operator import isCallable # deprecated, but documented alternative requires __mro__ to be defined in callable class

import MockMockMock
from MockMockMock import Mock, MockException
import MockMockMock.ArgumentCheckers as Checkers

class TestException( Exception ):
    pass

class PublicInterface( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def testMockMockMock( self ):
        ### @todo Remove MockEngine, SimpleExpectation, ExpectationGrouping from MockMockMock's public interface
        self.assertEqual( self.dir( MockMockMock ), [ "ArgumentCheckers", "ExpectationGrouping", "Mock", "MockEngine", "MockException", "SimpleExpectation" ] )

    def testMock( self ):
        self.assertEqual( self.dir( self.mock ), [ "alternative", "atomic", "expect", "object", "optional", "ordered", "repeated", "tearDown", "unordered" ] )
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
        ### @todo Maybe expose expected calls in mock.object.__dir__
        self.assertEqual( self.dir( self.mock.object ), [] )

    def dir( self, o ):
        return sorted( a for a in dir( o ) if not a.startswith( "_" ) )

class SingleExpectation( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def tearDown( self ):
        self.mock.tearDown()

    def testMethodCall( self ):
        self.mock.expect.foobar()
        self.mock.object.foobar()

    def testMethodCallWithSimpleArgument( self ):
        self.mock.expect.foobar( 42 )
        self.mock.object.foobar( 42 )

    def testMethodCallWithReturn( self ):
        returnValue = object()
        self.mock.expect.foobar().andReturn( returnValue )
        # Not only "==" but "is"
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

class SingleExpectationNotCalled( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

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

    def testMethodNotCalled( self ):
        self.mock.expect.foobar()
        with self.assertRaises( MockException ) as cm:
            self.mock.tearDown()
        self.assertEqual( cm.exception.message, "MyMock.foobar not called" )
        self.mock.object.foobar()
        self.mock.tearDown()

    def testPropertyNotCalled( self ):
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
        with self.assertRaises( MockException ) as cm:
            self.mock.object.barbaz()
        self.assertEqual( cm.exception.message, "MyMock.barbaz called instead of MyMock.foobar" )

    def testCallWithArgumentsNotExpectedFirst( self ):
        self.mock.expect.foobar( 42 )
        self.mock.expect.foobar( 43 )
        with self.assertRaises( MockException ) as cm:
            self.mock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "MyMock.foobar called with bad arguments" )

    def testManyCalls( self ):
        self.mock.expect.foobar( 1 )
        self.mock.expect.foobar( 2 )
        self.mock.expect.foobar( 3 )
        self.mock.expect.foobar( 4 )
        self.mock.expect.foobar( 5 )
        self.mock.expect.foobar( 6 )
        self.mock.object.foobar( 1 )
        self.mock.object.foobar( 2 )
        self.mock.object.foobar( 3 )
        self.mock.object.foobar( 4 )
        self.mock.object.foobar( 5 )
        self.mock.object.foobar( 6 )
        self.mock.tearDown()

class SequenceBetweenSeveralLinkedMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.m1 = Mock( "m1" )
        self.m2 = Mock( "m2", self.m1 )

    def testShortCorrectSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.m1.tearDown()

    def testShortInvertedSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        with self.assertRaises( MockException ) as cm:
            self.m2.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "m2.foobar called instead of m1.foobar" )

class SequenceBetweenSeveralIndependentMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.m1 = Mock( "m1" )
        self.m2 = Mock( "m2" )

    def testSameOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.m1.tearDown()
        self.m2.tearDown()

    def testOtherOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m2.object.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m1.tearDown()
        self.m2.tearDown()

class ArgumentCheckers( unittest.TestCase ):
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

    # def testIdentityChecker( self ):
    # def testTypeChecker( self ):
    # def testRangeChecker( self ):

    def testEqualityChecker( self ):
        c = Checkers.Equality( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } )
        self.assertTrue( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } ) )
        self.assertFalse( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 4 } ) )
        self.assertFalse( c( ( 1, 2, 4 ), { 1: 1, 2: 2, 3: 3 } ) )

unittest.main()
