import ArgumentChecking

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

    def nbRequiredCalls( self ):
        return 1

    def markExpectationCalled( self, expectation ):
        assert( self is not expectation )
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
        return self.withArguments( ArgumentChecking.Equality( args, kwds ) )

    def withArguments( self, checker ):
        self.__expectation.callPolicy = MethodCallPolicy( checker )
        return BasicExpectationProxy( self.__expectation )
