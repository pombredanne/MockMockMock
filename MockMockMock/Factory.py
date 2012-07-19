from _Details.Mock import Mock
from _Details.ExpectationGrouping import OrderedExpectationGroup, UnorderedExpectationGroup, AtomicExpectationGroup, OptionalExpectationGroup, AlternativeExpectationGroup, RepeatedExpectationGroup
from _Details.Engine import Engine

class Factory:
    def __init__( self ):
        self.__engine = Engine( OrderedExpectationGroup() )
        self.__mocks = list()

    def create( self, name ):
        mock = Mock( name, self.__engine )
        self.__mocks.append( mock )
        return mock

    def tearDown( self ):
        self.__engine.tearDown()

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
