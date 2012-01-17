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
        self.__mock.setExpectation( self.__expectation )

    def __call__( self, *args, **kwds ):
        call = MethodCallExpectation( self.__name, args, kwds )
        self.__mock.setExpectation( call )
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
        expectation = self.__mock.getExpectation()
        if expectation.name == name:
            if isinstance( expectation, MethodCallExpectation ):
                return expectation
            else:
                return expectation.action()
        else:
            raise MockException.MockException()

class MockImpl( object ):
    def __init__( self ):
        self.__expectation = None

    def setExpectation( self, expectation ):
        self.__expectation = expectation

    def getExpectation( self ):
        return self.__expectation

    def expect( self ):
        return Expecter( self )

    def object( self ):
        return Checker( self )
