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
        self.__parent = None
        self.__called = False

    def setParent( self, parent ):
        assert( self.__parent is None )
        self.__parent = parent

    def getCurrentPossibleExpectations( self ):
        if self.__called:
            return []
        else:
            return [ self ]

    def nbRequiredCalls( self ):
        if self.__called:
            return 0
        else:
            return 1

    def markExpectationCalled( self ):
        self.__called = True
        return self.__parent.rewindGroups()

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
