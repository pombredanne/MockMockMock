from MockEngine import MockEngine
from ExpectationGrouping import (
    OrderedExpectationGroup,
    UnorderedExpectationGroup,
    AtomicExpectationGroup,
    OptionalExpectationGroup,
    AlternativeExpectationGroup,
    RepeatedExpectationGroup
)

class Mock( object ):
    def __init__( self, name, brotherMock = None ):
        if brotherMock is None:
            self.__engine = MockEngine( OrderedExpectationGroup() )
        else:
            self.__engine = brotherMock.__engine
        self.__name = name

    @property
    def expect( self ):
        return self.__engine.expect( self.__name )

    @property
    def object( self ):
        return self.__engine.object( self.__name )

    @property
    def unordered( self ):
        return self.__engine.pushGroup( UnorderedExpectationGroup() )

    @property
    def ordered( self ):
        return self.__engine.pushGroup( OrderedExpectationGroup() )

    @property
    def atomic( self ):
        return self.__engine.pushGroup( AtomicExpectationGroup() )

    @property
    def optional( self ):
        return self.__engine.pushGroup( OptionalExpectationGroup() )

    @property
    def alternative( self ):
        return self.__engine.pushGroup( AlternativeExpectationGroup() )

    @property
    def repeated( self ):
        return self.__engine.pushGroup( RepeatedExpectationGroup() )

    def tearDown( self ):
        self.__engine.tearDown()
