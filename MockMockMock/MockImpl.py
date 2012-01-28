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

    def getCurrentPossibleExpectations( self ):
        return [ self ]

    def requiredCalls( self ):
        return [ self ]

    def removeExpectation( self, expectation ):
        return False

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
    def __init__( self, mock, expectations ):
        self.__expectations = expectations
        self.__mock = mock

    def __call__( self, *args, **kwds ):
        for expectation in self.__expectations:
            if expectation.callPolicy.checkCall( args, kwds ):
                self.__mock.removeExpectation( expectation )
                return expectation.action()
        else:
            raise MockException( self.__expectations[ 0 ].name + " called with bad arguments" )

class Checker:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        if name == "__dir__":
            raise AttributeError()
        calledName = self.__mock.name + "." + name
        expectations = self.__mock.getCurrentPossibleExpectations()

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
            return CallChecker( self.__mock, goodNamedExpectations )
        elif allGoodNamedExpectationsExpectNoCall:
            expectation = goodNamedExpectations[ 0 ]
            self.__mock.removeExpectation( expectation )
            return expectation.action()
        else:
            raise MockException( calledName + " is expected as a property and as a method call in an unordered group" )

class OrderedExpectationGroup:
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        possible = []
        for expectation in self.__expectations:
            possible += expectation.getCurrentPossibleExpectations()
            if len( expectation.requiredCalls() ) > 0:
                break
        return possible

    def removeExpectation( self, expectation ):
        if expectation is self.__expectations[ 0 ]:
            self.__expectations = self.__expectations[ 1 : ]
        else:
            if self.__expectations[ 0 ].removeExpectation( expectation ):
                self.__expectations = self.__expectations[ 1 : ]
        return len( self.__expectations ) == 0

    def requiredCalls( self ):
        required = []
        for expectation in self.__expectations:
            required += expectation.requiredCalls()
        return required

class UnorderedExpectationGroup:
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        possible = []
        for expectation in self.__expectations:
            possible += expectation.getCurrentPossibleExpectations()
        return possible

    def removeExpectation( self, expectation ):
        if expectation in self.__expectations:
            self.__expectations.remove( expectation )
        else:
            for e in self.__expectations:
                if e.removeExpectation( expectation ):
                    self.__expectations.remove( e )
                    break
        return len( self.__expectations ) == 0

    def requiredCalls( self ):
        required = []
        for expectation in self.__expectations:
            required += expectation.requiredCalls()
        return required

class FacultativeExpectationGroup:
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__expectations[ 0 ].getCurrentPossibleExpectations()

    def removeExpectation( self, expectation ):
        if expectation is self.__expectations[ 0 ]:
            self.__expectations = self.__expectations[ 1 : ]
        else:
            if self.__expectations[ 0 ].removeExpectation( expectation ):
                self.__expectations = self.__expectations[ 1 : ]
        return len( self.__expectations ) == 0

    def requiredCalls( self ):
        return []

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
            raise MockException( ", ".join( e.name for e in requiredCalls ) + " not called" )

    def startUnorderedGroup( self ):
        group = UnorderedExpectationGroup()
        self.addExpectation( group )
        self.__expectationGroups.append( group )

    def startOrderedGroup( self ):
        group = OrderedExpectationGroup()
        self.addExpectation( group )
        self.__expectationGroups.append( group )

    def startFacultativeGroup( self ):
        group = FacultativeExpectationGroup()
        self.addExpectation( group )
        self.__expectationGroups.append( group )

    def popGroup( self ):
        self.__expectationGroups.pop()

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

    def atomic( self ):
        self.__engine.startOrderedGroup()
        return StackPoper( self )

    def facultative( self ):
        self.__engine.startFacultativeGroup()
        return StackPoper( self )

    def popExpectationStack( self ):
        self.__engine.popGroup()
        pass

    def tearDown( self ):
        self.__engine.tearDown()
