from MockException import MockException
from SimpleExpectation import Expectation, ExpectationProxy

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

class MockEngine( object ):
    def __init__( self, initialGroup ):
        self.__currentGroup = initialGroup

    # expect
    def expect( self, mockName ):
        return Expecter( self, mockName )

    def addExpectation( self, name ):
        # Note that accepting name == "__call__" allows the mock object to be callable with no specific code
        expectation = Expectation( name )
        self.__addExpectation( expectation )
        return ExpectationProxy( expectation )

    def __addExpectation( self, expectation ):
        self.__currentGroup.addExpectation( expectation )

    def pushGroup( self, group ):
        self.__addExpectation( group )
        group.setParent( self.__currentGroup )
        self.__currentGroup = group
        return MockEngine.StackPoper( self )

    class StackPoper:
        def __init__( self, engine ):
            self.__engine = engine

        def __enter__( self ):
            pass

        def __exit__( self, a, b, c ):
            self.__engine.popGroup()

    def popGroup( self ):
        self.__currentGroup = self.__currentGroup.parent

    # call
    def object( self, mockName ):
        return Checker( self, mockName )

    def getCurrentPossibleExpectations( self ):
        return self.__currentGroup.getCurrentPossibleExpectations()

    def checkExpectation( self, calledName ):
        expectations = self.getCurrentPossibleExpectations()

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
            return CallChecker( self, goodNamedExpectations )
        elif allGoodNamedExpectationsExpectNoCall:
            expectation = goodNamedExpectations[ 0 ]
            self.markExpectationCalled( expectation )
            return expectation.action()
        else:
            raise MockException( calledName + " is expected as a property and as a method call in an unordered group" )

    def checkExpectationCall( self, expectations, args, kwds ):
        for expectation in expectations:
            if expectation.callPolicy.checkCall( args, kwds ):
                self.markExpectationCalled( expectation )
                return expectation.action()
        raise MockException( expectations[ 0 ].name + " called with bad arguments" )

    def markExpectationCalled( self, expectation ):
        self.__currentGroup.markExpectationCalled( expectation )

    def tearDown( self ):
        requiredCalls = self.__currentGroup.nbRequiredCalls()
        if requiredCalls:
            raise MockException( ", ".join( self.__currentGroup.getRequiredCallsExamples() ) + " not called" )
