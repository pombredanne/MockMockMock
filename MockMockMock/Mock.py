import MockImpl

class Mock( object ):
    def __init__( self, name, brotherMock = None ):
        if brotherMock is None:
            self.__impl = MockImpl.MockImpl( name, None )
        else:
            self.__impl = MockImpl.MockImpl( name, brotherMock.__impl )

    @property
    def expect( self ):
        return self.__impl.expect()

    @property
    def object( self ):
        return self.__impl.object()

    def tearDown( self ):
        return self.__impl.tearDown()
