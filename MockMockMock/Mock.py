class Mock( object ):
    def __init__( self, name, engine ):
        self.__name = name
        self.__engine = engine

    @property
    def expect( self ):
        return self.__engine.expect( self.__name )

    @property
    def object( self ):
        return self.__engine.object( self.__name )
