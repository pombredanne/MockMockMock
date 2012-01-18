import MockImpl

class Mock( object ):
    def __init__( self ):
        self.__impl = MockImpl.MockImpl()

    @property
    def expect( self ):
        return self.__impl.expect()

    @property
    def object( self ):
        return self.__impl.object()

    def tearDown( self ):
        return self.__impl.tearDown()
