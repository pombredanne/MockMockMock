from MockException import MockException
from SimpleExpectation import Expectation, ExpectationProxy

class Expecter:
    def __init__( self, engine, mockName ):
        self.__engine = engine
        self.__mockName = mockName

    def __getattr__( self, name ):
        # Note that accepting name == "__call__" allows the mock object to be callable with no specific code
        if name == "__dir__":
            raise AttributeError()
        expectation = Expectation( self.__mockName + "." + name )
        self.__engine.addExpectation( expectation )
        return ExpectationProxy( expectation )

class CallChecker:
    def __init__( self, engine, expectations ):
        self.__engine = engine
        self.__expectations = expectations

    def __call__( self, *args, **kwds ):
        for expectation in self.__expectations:
            if expectation.callPolicy.checkCall( args, kwds ):
                self.__engine.markExpectationCalled( expectation )
                return expectation.action()
        raise MockException( self.__expectations[ 0 ].name + " called with bad arguments" )

class Checker:
    def __init__( self, engine, mockName ):
        self.__engine = engine
        self.__mockName = mockName

    def __getattr__( self, name ):
        if name == "__dir__":
            raise AttributeError()
        calledName = self.__mockName + "." + name
        expectations = self.__engine.getCurrentPossibleExpectations()

        goodNamedExpectations = []
        allGoodNamedExpectationsExpectCall = True
        allGoodNamedExpectationsExpectNoCall = True

        for expectation in expectations:
            if expectation.name == calledName:
                goodNamedExpectations.append( expectation )
                if expectation.callPolicy.expectsCall:
                    allGoodNamedExpectationsExpectNoCall = False
                else:
                    allGoodNamedExpectationsExpectCall = False

        if len( goodNamedExpectations ) == 0:
            raise MockException( calledName + " called instead of " + " or ".join( e.name for e in expectations ) )

        if allGoodNamedExpectationsExpectCall:
            return CallChecker( self.__engine, goodNamedExpectations )
        elif allGoodNamedExpectationsExpectNoCall:
            expectation = goodNamedExpectations[ 0 ]
            self.__engine.markExpectationCalled( expectation )
            return expectation.action()
        else:
            raise MockException( calledName + " is expected as a property and as a method call in an unordered group" )

class MockEngine( object ):
    class StackPoper:
        def __init__( self, engine ):
            self.__engine = engine

        def __enter__( self ):
            pass

        def __exit__( self, a, b, c ):
            self.__engine.popGroup()

    def __init__( self, initialGroup ):
        self.__expectationGroups = [ initialGroup ]

    def expect( self, mockName ):
        return Expecter( self, mockName )

    def object( self, mockName ):
        return Checker( self, mockName )

    def addExpectation( self, expectation ):
        self.__expectationGroups[ -1 ].addExpectation( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__singleGroup.getCurrentPossibleExpectations()

    def markExpectationCalled( self, expectation ):
        self.__singleGroup.markExpectationCalled( expectation )

    @property
    def __singleGroup( self ):
        assert( len( self.__expectationGroups ) == 1 )
        return self.__expectationGroups[ 0 ]

    def tearDown( self ):
        requiredCalls = self.__singleGroup.nbRequiredCalls()
        if requiredCalls:
            raise MockException( ", ".join( self.__singleGroup.getRequiredCallsExamples() ) + " not called" )

    def pushGroup( self, group ):
        self.addExpectation( group )
        self.__expectationGroups.append( group )
        return MockEngine.StackPoper( self )

    def popGroup( self ):
        self.__expectationGroups.pop()
