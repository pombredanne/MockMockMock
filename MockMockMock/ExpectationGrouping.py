class OrderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
            if expectation.nbRequiredCalls() > 0:
                break
        return possible

class UnorderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
        return possible

class AllCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        required = 0
        for expectation in expectations:
            required += expectation.nbRequiredCalls()
        return required

class AnyCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        return 0

ExactlyOneCompletionPolicy = AllCompletionPolicy
RepeatedCompletionPolicy = AllCompletionPolicy

class UnstickyStickynessPolicy:
    pass

class StickyStickynessPolicy:
    pass

class ExpectationGroup:
    def __init__( self, ordering, completion, stickyness ):
        self.__ordering = ordering
        self.__completion = completion
        self.__stickyness = stickyness
        self.__parent = None
        self.__expectations = []

    def setParent( self, parent ):
        assert( self.__parent is None )
        self.__parent = parent

    @property
    def parent( self ):
        assert( self.__parent is not None )
        return self.__parent

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__ordering.getCurrentPossibleExpectations( self.__expectations )

    def markExpectationCalled( self, expectation ):
        if expectation in self.__expectations:
            self.__expectations.remove( expectation )
        else:
            for e in self.__expectations:
                if e.markExpectationCalled( expectation ):
                    self.__expectations.remove( e )
                    break
        return len( self.__expectations ) == 0

    def nbRequiredCalls( self ):
        return self.__completion.nbRequiredCalls( self.__expectations )

    def getRequiredCallsExamples( self ):
        return [ "MyMock.foobar" ]

def makeGroup( ordering, completion, stickyness ):
    class Group( ExpectationGroup ):
        def __init__( self ):
            ExpectationGroup.__init__( self, ordering(), completion(), stickyness() )

    return Group

OrderedExpectationGroup = makeGroup( OrderedOrderingPolicy, AllCompletionPolicy, UnstickyStickynessPolicy )
UnorderedExpectationGroup = makeGroup( UnorderedOrderingPolicy, AllCompletionPolicy, UnstickyStickynessPolicy )
AtomicExpectationGroup = makeGroup( OrderedOrderingPolicy, AllCompletionPolicy, StickyStickynessPolicy )
OptionalExpectationGroup = makeGroup( OrderedOrderingPolicy, AnyCompletionPolicy, UnstickyStickynessPolicy )
AlternativeExpectationGroup = makeGroup( UnorderedOrderingPolicy, ExactlyOneCompletionPolicy, UnstickyStickynessPolicy )
RepeatedExpectationGroup = makeGroup( OrderedOrderingPolicy, RepeatedCompletionPolicy, UnstickyStickynessPolicy )
