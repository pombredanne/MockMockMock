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

    @property
    def unordered( self ):
        return self.__impl.unordered()

    @property
    def ordered( self ):
        return self.__impl.ordered()

    @property
    def atomic( self ):
        return self.__impl.atomic()

    @property
    def optional( self ):
        return self.__impl.optional()

    @property
    def alternative( self ):
        return self.__impl.alternative()

    @property
    def repeated( self ):
        return self.__impl.repeated()

    def tearDown( self ):
        return self.__impl.tearDown()
