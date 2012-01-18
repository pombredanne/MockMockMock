import MockException

class ArgumentsChecker:
    def __init__( self, args, kwds ):
        self.__args = args
        self.__kwds = kwds

    def check( self, args, kwds ):
        if self.__args != args or self.__kwds != kwds:
            raise MockException.MockException()

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

class MethodCallExpectation( Actionable ):
    def __init__( self, name, args, kwds ):
        Actionable.__init__( self )
        self.__name = name
        self.__argumentsChecker = ArgumentsChecker( args, kwds )

    @property
    def name( self ):
        return self.__name

    def __call__( self, *args, **kwds ):
        self.__argumentsChecker.check( args, kwds )
        return self.action()

class PropertyExpectation( Actionable ):
    def __init__( self, name ):
        self.__name = name

    @property
    def name( self ):
        return self.__name

class AttributeExpecter:
    def __init__( self, mock, name ):
        self.__mock = mock
        self.__name = name
        self.__expectation = PropertyExpectation( name )
        self.__mock.addExpectation( self.__expectation )

    def __call__( self, *args, **kwds ):
        call = MethodCallExpectation( self.__name, args, kwds )
        self.__mock.replaceExpectation( self.__expectation, call )
        return call

    def andReturn( self, value ):
        self.__expectation.andReturn( value )

    def andRaise( self, exception ):
        self.__expectation.andRaise( exception )

    def andExecute( self, callable ):
        self.__expectation.andExecute( callable )

class Expecter:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        return AttributeExpecter( self.__mock, name )
       
class Checker:
    def __init__( self, mock ):
        self.__mock = mock

    def __getattr__( self, name ):
        expectation = self.__mock.getLastExpectation()
        if expectation.name == name:
            if isinstance( expectation, MethodCallExpectation ):
                return expectation
            else:
                return expectation.action()
        else:
            raise MockException.MockException()

class MockImpl( object ):
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def replaceExpectation( self, oldExpectation, newExpectation ):
        assert( self.__expectations[ -1 ] is oldExpectation )
        self.__expectations[ -1 ] = newExpectation

    def getLastExpectation( self ):
        expectation = self.__expectations[ 0 ]
        self.__expectations = self.__expectations[ 1: ]
        return expectation

    def expect( self ):
        return Expecter( self )

    def object( self ):
        return Checker( self )
