import Mock
import ExpectationGrouping
import Details.Engine

class Factory:
    def __init__( self ):
        self.__engine = Details.Engine.Engine( ExpectationGrouping.OrderedExpectationGroup() )
        self.__mocks = list()

    def create( self, name ):
        mock = Mock.Mock( name, self.__engine )
        self.__mocks.append( mock )
        return mock

    def tearDown( self ):
        self.__engine.tearDown()

    @property
    def unordered( self ):
        return self.__engine.pushGroup( ExpectationGrouping.UnorderedExpectationGroup() )

    @property
    def ordered( self ):
        return self.__engine.pushGroup( ExpectationGrouping.OrderedExpectationGroup() )

    @property
    def atomic( self ):
        return self.__engine.pushGroup( ExpectationGrouping.AtomicExpectationGroup() )

    @property
    def optional( self ):
        return self.__engine.pushGroup( ExpectationGrouping.OptionalExpectationGroup() )

    @property
    def alternative( self ):
        return self.__engine.pushGroup( ExpectationGrouping.AlternativeExpectationGroup() )

    @property
    def repeated( self ):
        return self.__engine.pushGroup( ExpectationGrouping.RepeatedExpectationGroup() )
