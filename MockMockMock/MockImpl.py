from MockException import MockException

class Actionable( object ):
    def __init__( self ):
        self.andReturn( None )

    def andReturn( self, value ):
        self.andExecute( lambda : value )
        return self

    def andRaise( self, exception ):
        def Raise(): raise exception
        self.andExecute( Raise )
        return self

    def andExecute( self, callable ):
        self.__action = callable
        return self

    @property
    def action( self ):
        return self.__action

class PropertyCallPolicy( object ):
    @property
    def expectsCall( self ):
        return False

class MethodCallPolicy( object ):
    def __init__( self, args, kwds ):
        self.__args = args
        self.__kwds = kwds

    @property
    def expectsCall( self ):
        return True

    def checkCall( self, args, kwds ):
        return self.__args == args and self.__kwds == kwds

class Expectation( Actionable ):
    def __init__( self, name ):
        Actionable.__init__( self )
        self.name = name
        self.callPolicy = PropertyCallPolicy()

    def __call__( self, *args, **kwds ):
        self.callPolicy = MethodCallPolicy( args, kwds )
        return self

    @property
    def expectsCall( self ):
        return self.callPolicy.expectsCall

class Expecter:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        expectation = Expectation( name )
        self.__mock.addExpectation( expectation )
        return expectation

class CallChecker:
    def __init__( self, expectation ):
        self.__expectation = expectation

    def __call__( self, *args, **kwds ):
        if not self.__expectation.callPolicy.checkCall( args, kwds ):
            raise MockException()
        return self.__expectation.action()

class Checker:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        expectation = self.__mock.getLastExpectation()
        if expectation.name == name:
            if expectation.expectsCall:
                return CallChecker( expectation )
            else:
                return expectation.action()
        else:
            raise MockException()

class MockImpl( object ):
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getLastExpectation( self ):
        expectation = self.__expectations[ 0 ]
        self.__expectations = self.__expectations[ 1: ]
        return expectation

    def expect( self ):
        return Expecter( self )

    def object( self ):
        return Checker( self )
