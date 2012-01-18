from MockException import MockException

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

class Expectation( object ):
    def __init__( self, name ):
        self.name = name
        self.callPolicy = PropertyCallPolicy()
        self.action = lambda : None

    @property
    def expectsCall( self ):
        return self.callPolicy.expectsCall

class AndableExpectationProxy:
    def __init__( self, expectation ):
        self.__expectation = expectation

    def andReturn( self, value ):
        return self.andExecute( lambda : value )

    def andRaise( self, exception ):
        def Raise(): raise exception
        return self.andExecute( Raise )

    def andExecute( self, callable ):
        self.__expectation.action = callable
        return AndedExpectationProxy( self.__expectation )

class CallableExpectationProxy:
    def __init__( self, expectation ):
        self.__expectation = expectation

    def __call__( self, *args, **kwds ):
        return self.__withArguments( args, kwds )

    def withArguments( self, *args, **kwds ):
        return self.__withArguments( args, kwds )

    def __withArguments( self, args, kwds ):
        self.__expectation.callPolicy = MethodCallPolicy( args, kwds )
        return CalledExpectationProxy( self.__expectation )

class ExpectationProxy( AndableExpectationProxy, CallableExpectationProxy ) :
    def __init__( self, expectation ):
        AndableExpectationProxy.__init__( self, expectation )
        CallableExpectationProxy.__init__( self, expectation )

class CalledExpectationProxy( AndableExpectationProxy ):
    def __init__( self, expectation ):
        AndableExpectationProxy.__init__( self, expectation )

class AndedExpectationProxy:
    def __init__( self, expectation ):
        pass

class Expecter:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        expectation = Expectation( name )
        self.__mock.addExpectation( expectation )
        return ExpectationProxy( expectation )

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
