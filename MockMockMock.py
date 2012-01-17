class MockException( Exception ):
    pass

class ArgumentsChecker:
    def __init__( self, args, kwds ):
        self.__args = args
        self.__kwds = kwds

    def check( self, args, kwds ):
        if self.__args != args or self.__kwds != kwds:
            raise MockException()

class Actionable( object ):
    def __init__( self ):
        self.andReturn( None )

    def andReturn( self, value ):
        self.andExecute( lambda : value )

    def andRaise( self, exception ):
        def Raise(): raise exception
        self.andExecute( Raise )

    def andExecute( self, callable ):
        self.__action = callable

    @property
    def action( self ):
        return self.__action

class CallDescription( Actionable ):
    def __init__( self, name, args, kwds ):
        Actionable.__init__( self )
        self.__name = name
        self.__argumentsChecker = ArgumentsChecker( args, kwds )

    @property
    def name( self ):
        return self.__name

    @property
    def arguments( self ):
        return self.__argumentsChecker

class ExpectedCall:
    def __init__( self, mock, name ):
        self.__mock = mock
        self.__name = name

    def __call__( self, *args, **kwds ):
        call = CallDescription( self.__name, args, kwds )
        self.__mock.addExpectation( call )
        return call

class Expecter:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        return ExpectedCall( self.__mock, name )

class CallChecker:
    def __init__( self, mock, expectation ):
        self.__mock = mock
        self.__expectation = expectation

    def __call__( self, *args, **kwds ):
        self.__expectation.arguments.check( args, kwds )
        return self.__expectation.action()

class Object:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        expectation = self.__mock.getExpectations()[ 0 ]
        if expectation.name == name:
            return CallChecker( self.__mock, expectation )
        else:
            raise MockException()

class MockImpl( object ):
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, call ):
        self.__expectations.append( call )

    def removeExpectation( self ):
        self.__expectations = self.__expectations[ 1: ]

    def getExpectations( self ):
        return self.__expectations

class Mock( object ):
    def __init__( self ):
        self.__impl = MockImpl()

    @property
    def expect( self ):
        return Expecter( self.__impl )

    @property
    def object( self ):
        return Object( self.__impl )

    def tearDown( self ):
        pass
