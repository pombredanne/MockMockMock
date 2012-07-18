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
        self.factory = MockMockMock.Factory()
        self.mock = self.factory.create( "MyMock" )

    def testMockMockMock( self ):
        self.assertEqual( self.dir( MockMockMock ), [
            "ArgumentChecking",
            "Details",
            "Expectation", ### @todo Remove
            "ExpectationGrouping", ### @todo Remove
            "Factory",
            "Mock", ### @todo Remove
            "MockException",
            "TestCase",
        ] )

    def testFactory( self ):
        self.assertEqual( self.dir( self.factory ), [ "alternative", "atomic", "create", "optional", "ordered", "repeated", "tearDown", "unordered" ] )
        self.assertFalse( isCallable( self.factory ) )

    def testMock( self ):
        self.assertEqual( self.dir( self.mock ), [ "expect", "object" ] )
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

class SingleExpectation( MockMockMock.TestCase ):
    def setUp( self ):
        MockMockMock.TestCase.setUp( self )
        self.mock = self.createMock( "MyMock" )

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
        self.factory = MockMockMock.Factory()
        self.mock = self.factory.create( "MyMock" )

    def testMethodCallWithBadArgument( self ):
        self.mock.expect.foobar( 42 )
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.mock.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "MyMock.foobar called with bad arguments" )

    def testMethodCallWithBadName( self ):
        self.mock.expect.foobar()
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.mock.object.barbaz()
        self.assertEqual( cm.exception.message, "MyMock.barbaz called instead of MyMock.foobar" )

    def testMethodCallWithBadName2( self ):
        self.mock.expect.foobar2()
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.mock.object.barbaz()
        self.assertEqual( cm.exception.message, "MyMock.barbaz called instead of MyMock.foobar2" )

    def testPropertyWithBadName( self ):
        self.mock.expect.foobar.andReturn( 42 )
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.mock.object.barbaz
        self.assertEqual( cm.exception.message, "MyMock.barbaz called instead of MyMock.foobar" )

    def testMethodNotCalled( self ):
        self.mock.expect.foobar()
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.factory.tearDown()
        self.assertEqual( cm.exception.message, "MyMock.foobar not called" )
        self.mock.object.foobar()
        self.factory.tearDown()

    def testPropertyNotCalled( self ):
        self.mock.expect.foobar
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.factory.tearDown()
        self.assertEqual( cm.exception.message, "MyMock.foobar not called" )
        self.mock.object.foobar
        self.factory.tearDown()

class ExpectationSequence( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.factory = MockMockMock.Factory()
        self.mock = self.factory.create( "MyMock" )

    def testTwoCalls( self ):
        self.mock.expect.foobar()
        self.mock.expect.barbaz()
        self.mock.object.foobar()
        self.mock.object.barbaz()
        self.factory.tearDown()

    def testCallNotExpectedFirst( self ):
        self.mock.expect.foobar()
        self.mock.expect.barbaz()
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.mock.object.barbaz()
        self.assertEqual( cm.exception.message, "MyMock.barbaz called instead of MyMock.foobar" )

    def testCallWithArgumentsNotExpectedFirst( self ):
        self.mock.expect.foobar( 42 )
        self.mock.expect.foobar( 43 )
        with self.assertRaises( MockMockMock.MockException ) as cm:
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
        self.factory.tearDown()

class SequenceBetweenSeveralLinkedMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.factory = MockMockMock.Factory()
        self.m1 = self.factory.create( "m1" )
        self.m2 = self.factory.create( "m2" )

    def testShortCorrectSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.factory.tearDown()

    def testShortInvertedSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        with self.assertRaises( MockMockMock.MockException ) as cm:
            self.m2.object.foobar( 43 )
        self.assertEqual( cm.exception.message, "m2.foobar called instead of m1.foobar" )

class SequenceBetweenSeveralIndependentMocks( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.factory1 = MockMockMock.Factory()
        self.factory2 = MockMockMock.Factory()
        self.m1 = self.factory1.create( "m1" )
        self.m2 = self.factory2.create( "m2" )

    def testSameOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.m2.object.foobar( 43 )
        self.factory1.tearDown()
        self.factory2.tearDown()

    def testOtherOrderSequence( self ):
        self.m1.expect.foobar( 42 )
        self.m2.expect.foobar( 43 )
        self.m2.object.foobar( 43 )
        self.m1.object.foobar( 42 )
        self.factory1.tearDown()
        self.factory2.tearDown()

class ArgumentCheckers( unittest.TestCase ):
    def testCheckerIsUsedByCall( self ):
        # We use a mock...
        checker = MockMockMock.Factory().create( "checker" )
        checker.expect( ( 12, ), {} ).andReturn( True )
        checker.expect( ( 13, ), {} ).andReturn( False )
    
        # ...to test a mock!
        m = MockMockMock.Factory().create( "m" )
        m.expect.foobar.withArguments( checker.object ).andReturn( 42 )
        m.expect.foobar.withArguments( checker.object ).andReturn( 43 )
        self.assertEqual( m.object.foobar( 12 ), 42 )
        with self.assertRaises( MockMockMock.MockException ) as cm:
            m.object.foobar( 13 )
        self.assertEqual( cm.exception.message, "m.foobar called with bad arguments" )

    # def testIdentityChecker( self ):
    # def testTypeChecker( self ):
    # def testRangeChecker( self ):

    def testEqualityChecker( self ):
        c = MockMockMock.ArgumentChecking.Equality( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } )
        self.assertTrue( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 3 } ) )
        self.assertFalse( c( ( 1, 2, 3 ), { 1: 1, 2: 2, 3: 4 } ) )
        self.assertFalse( c( ( 1, 2, 4 ), { 1: 1, 2: 2, 3: 3 } ) )

class Ordering( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.factory = MockMockMock.Factory()
        self.mock = self.factory.create( "MyMock" )

    def testUnorderedGroupOfSameMethod( self ):
        with self.factory.unordered:
            self.mock.expect.foobar( 1 ).andReturn( 11 )
            self.mock.expect.foobar( 1 ).andReturn( 13 )
            self.mock.expect.foobar( 2 ).andReturn( 12 )
            self.mock.expect.foobar( 1 ).andReturn( 14 )
        self.assertEqual( self.mock.object.foobar( 2 ), 12 )
        self.assertEqual( self.mock.object.foobar( 1 ), 11 )
        self.assertEqual( self.mock.object.foobar( 1 ), 13 )
        self.assertEqual( self.mock.object.foobar( 1 ), 14 )
        self.factory.tearDown()

    ### @todo Allow unordered property and method calls on the same name: difficult
    def testUnorderedGroupOfSameMethodAndProperty( self ):
        with self.assertRaises( MockMockMock.MockException ) as cm:
            with self.factory.unordered:
                self.mock.expect.foobar()
                self.mock.expect.foobar
            self.mock.object.foobar
        self.assertEqual( cm.exception.message, "MyMock.foobar is expected as a property and as a method call in an unordered group" )

    def testUnorderedGroupOfSamePropertyAndMethod( self ):
        with self.assertRaises( MockMockMock.MockException ) as cm:
            with self.factory.unordered:
                self.mock.expect.foobar
                self.mock.expect.foobar()
            self.mock.object.foobar()
        self.assertEqual( cm.exception.message, "MyMock.foobar is expected as a property and as a method call in an unordered group" )

unittest.main()
