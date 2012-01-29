from MockException import MockException
from Expectation import Expectation
import ArgumentChecking

class Expecter:
    def __init__( self, engine, mockName ):
        self.__engine = engine
        self.__mockName = mockName

    def __getattr__( self, name ):
        if name == "__dir__": raise AttributeError()
        return self.__engine.addExpectation( self.__mockName + "." + name )

class Checker:
    def __init__( self, engine, mockName ):
        self.__engine = engine
        self.__mockName = mockName

    def __getattr__( self, name ):
        if name == "__dir__": raise AttributeError()
        return self.__engine.checkExpectation( self.__mockName + "." + name )

class CallChecker:
    def __init__( self, engine, expectations ):
        self.__engine = engine
        self.__expectations = expectations

    def __call__( self, *args, **kwds ):
        return self.__engine.checkExpectationCall( self.__expectations, args, kwds )

class BasicExpectationProxy:
    def __init__( self, expectation ):
        self.__expectation = expectation

    def andReturn( self, value ):
        return self.andExecute( lambda : value )

    def andRaise( self, exception ):
        def Raise(): raise exception
        return self.andExecute( Raise )

    def andExecute( self, action ):
        self.__expectation.setAction( action )
        return None

class CallableExpectationProxy( BasicExpectationProxy ):
    def __init__( self, expectation ):
        BasicExpectationProxy.__init__( self, expectation )
        self.__expectation = expectation

    def __call__( self, *args, **kwds ):
        return self.withArguments( ArgumentChecking.Equality( args, kwds ) )

    def withArguments( self, checker ):
        self.__expectation.expectCall( checker )
        return BasicExpectationProxy( self.__expectation )

class MockEngine( object ):
    def __init__( self, initialGroup ):
        self.__currentGroup = initialGroup

    # expect
    def expect( self, mockName ):
        return Expecter( self, mockName )

    def addExpectation( self, name ):
        # Note that accepting name == "__call__" allows the mock object to be callable with no specific code
        expectation = Expectation( name )
        self.__currentGroup.addExpectation( expectation )
        return CallableExpectationProxy( expectation )

    def pushGroup( self, group ):
        self.__currentGroup.addGroup( group )
        self.__currentGroup = group
        return MockEngine.StackPoper( self )

    class StackPoper:
        def __init__( self, engine ): self.__engine = engine
        def __enter__( self ): pass
        def __exit__( self, *ignored ): self.__engine.popGroup()

    def popGroup( self ):
        self.__currentGroup = self.__currentGroup.parent

    # call
    def object( self, mockName ):
        return Checker( self, mockName )

    def checkExpectation( self, calledName ):
        expectations = self.__currentGroup.getCurrentPossibleExpectations()

        goodNamedExpectations = []
        allGoodNamedExpectationsExpectCall = True
        allGoodNamedExpectationsExpectNoCall = True

        for expectation in expectations:
            if expectation.name == calledName:
                goodNamedExpectations.append( expectation )
                if expectation.expectsCall():
                    allGoodNamedExpectationsExpectNoCall = False
                else:
                    allGoodNamedExpectationsExpectCall = False

        if len( goodNamedExpectations ) == 0:
            raise MockException( calledName + " called instead of " + " or ".join( e.name for e in expectations ) )

        if allGoodNamedExpectationsExpectCall:
            return CallChecker( self, goodNamedExpectations )
        elif allGoodNamedExpectationsExpectNoCall:
            expectation = goodNamedExpectations[ 0 ]
            return self.__callExpectation( expectation )
        else:
            raise MockException( calledName + " is expected as a property and as a method call in an unordered group" )

    def checkExpectationCall( self, expectations, args, kwds ):
        for expectation in expectations:
            if expectation.checkCall( args, kwds ):
                return self.__callExpectation( expectation )
        raise MockException( expectations[ 0 ].name + " called with bad arguments" )

    def __callExpectation( self, expectation ):
        returnValue, self.__currentGroup = expectation.call()
        return returnValue

    def tearDown( self ):
        requiredCalls = self.__currentGroup.nbRequiredCalls()
        if requiredCalls:
            raise MockException( ", ".join( self.__currentGroup.getRequiredCallsExamples() ) + " not called" )
