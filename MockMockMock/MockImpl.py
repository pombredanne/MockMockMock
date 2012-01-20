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
        return self.__withArguments( args, kwds )

    def withArguments( self, *args, **kwds ):
        return self.__withArguments( args, kwds )

    def __withArguments( self, args, kwds ):
        self.__expectation.callPolicy = MethodCallPolicy( args, kwds )
        return BasicExpectationProxy( self.__expectation )

class Expecter:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
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
        expectation = self.__mock.getLastExpectation()
        calledName = self.__mock.name + "." + name
        if expectation.name == calledName:
            if expectation.expectsCall:
                return CallChecker( self.__mock, expectation )
            else:
                return expectation.action()
        else:
            raise MockException( calledName + " called instead of " + expectation.name )

class MockEngine( object ):
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getLastExpectation( self ):
        expectation = self.__expectations[ 0 ]
        self.__expectations = self.__expectations[ 1: ]
        return expectation
            
    def tearDown( self ):
        if len( self.__expectations ) > 0:
            raise MockException( self.__expectations[ 0 ].name + " not called" )

class MockImpl( object ):
    def __init__( self, name, brotherMock ):
        if brotherMock is None:
            self.__engine = MockEngine()
        else:
            self.__engine = brotherMock.__engine
        self.name = name

    def addExpectation( self, expectation ):
        self.__engine.addExpectation( expectation )

    def getLastExpectation( self ):
        return self.__engine.getLastExpectation()

    def expect( self ):
        return Expecter( self )

    def object( self ):
        return Checker( self )

    def tearDown( self ):
        self.__engine.tearDown()
