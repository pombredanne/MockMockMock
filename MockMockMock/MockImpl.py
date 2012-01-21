from MockException import MockException
import ArgumentCheckers

class PropertyCallPolicy( object ):
    @property
    def expectsCall( self ):
        return False

class MethodCallPolicy( object ):
    def __init__( self, checker ):
        self.__checker = checker

    @property
    def expectsCall( self ):
        return True

    def checkCall( self, args, kwds ):
        return self.__checker( args, kwds )

class Expectation( object ):
    def __init__( self, name ):
        self.name = name
        self.callPolicy = PropertyCallPolicy()
        self.action = lambda : None

    @property
    def expectsCall( self ):
        return self.callPolicy.expectsCall

class BasicExpectationProxy:
    def __init__( self, expectation ):
        self.__expectation = expectation

    def andReturn( self, value ):
        return self.andExecute( lambda : value )

    def andRaise( self, exception ):
        def Raise(): raise exception
        return self.andExecute( Raise )

    def andExecute( self, callable ):
        self.__expectation.action = callable
        return None

class ExpectationProxy( BasicExpectationProxy ):
    def __init__( self, expectation ):
        BasicExpectationProxy.__init__( self, expectation )
        self.__expectation = expectation

    def __call__( self, *args, **kwds ):
        return self.withArguments( ArgumentCheckers.Equality( args, kwds ) )

    def withArguments( self, checker ):
        self.__expectation.callPolicy = MethodCallPolicy( checker )
        return BasicExpectationProxy( self.__expectation )

class Expecter:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        # Note that accepting name == "__call__" allows the mock object to be callable with no specific code
        if name == "__dir__":
            raise AttributeError()
        expectation = Expectation( self.__mock.name + "." + name )
        self.__mock.addExpectation( expectation )
        return ExpectationProxy( expectation )

class CallChecker:
    def __init__( self, mock, expectation ):
        self.__expectation = expectation
        self.__mock = mock

    def __call__( self, *args, **kwds ):
        if not self.__expectation.callPolicy.checkCall( args, kwds ):
            raise MockException( self.__expectation.name + " called with bad arguments" )
        return self.__expectation.action()

class Checker:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        if name == "__dir__":
            raise AttributeError()
        calledName = self.__mock.name + "." + name
        expectations = self.__mock.getCurrentPossibleExpectations()
        for expectation in expectations:
            if expectation.name == calledName:
                self.__mock.removeExpectation( expectation )
                if expectation.expectsCall:
                    return CallChecker( self.__mock, expectation )
                else:
                    return expectation.action()
        else:
            raise MockException( calledName + " called instead of " + expectation.name )

class OrderedExpectationGroup:
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__expectations[ 0 : 1 ]

    def removeExpectation( self, expectation ):
        assert( expectation is self.__expectations[ 0 ] )
        self.__expectations = self.__expectations[ 1 : ]

    def requiredCalls( self ):
        return [ e.name for e in self.__expectations ]

class MockEngine( object ):
    def __init__( self ):
        self.__expectationGroups = [ OrderedExpectationGroup() ]

    def addExpectation( self, expectation ):
        self.__expectationGroups[ -1 ].addExpectation( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__singleGroup.getCurrentPossibleExpectations()

    def removeExpectation( self, expectation ):
        self.__singleGroup.removeExpectation( expectation )

    @property
    def __singleGroup( self ):
        assert( len( self.__expectationGroups ) == 1 )
        return self.__expectationGroups[ 0 ]
            
    def tearDown( self ):
        requiredCalls = self.__singleGroup.requiredCalls()
        if len( requiredCalls ) > 0:
            raise MockException( ", ".join( requiredCalls ) + " not called" )

class StackPoper:
    def __init__( self, mock ):
        self.__mock = mock

    def __enter__( self ):
        pass
        
    def __exit__( self, a, b, c ):
        self.__mock.popExpectationStack()
            
class MockImpl( object ):
    def __init__( self, name, brotherMock ):
        if brotherMock is None:
            self.__engine = MockEngine()
        else:
            self.__engine = brotherMock.__engine
        self.name = name

    def addExpectation( self, expectation ):
        self.__engine.addExpectation( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__engine.getCurrentPossibleExpectations()

    def removeExpectation( self, expectation ):
        self.__engine.removeExpectation( expectation )

    def expect( self ):
        return Expecter( self )

    def object( self ):
        return Checker( self )

    def unordered( self ):
        self.__engine.startUnorderedGroup()
        return StackPoper( self )

    def ordered( self ):
        self.__engine.startOrderedGroup()
        return StackPoper( self )

    def popExpectationStack( self ):
        self.__engine.popGroup()
        pass

    def tearDown( self ):
        self.__engine.tearDown()
