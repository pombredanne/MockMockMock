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

    def acceptsMoreCalls( self, expectations ):
        return any( len(expectation.getCurrentPossibleExpectations() ) != 0 for expectation in expectations )

class AnyCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        return 0

    def acceptsMoreCalls( self, expectations ):
        return True

class ExactlyOneCompletionPolicy:
    def nbRequiredCalls( self, expectations ):
        required = 1
        for expectation in expectations:
            if len( expectation.getCurrentPossibleExpectations() ) == 0:
                required = 0
        return required

    def acceptsMoreCalls( self, expectations ):
        return self.nbRequiredCalls( expectations ) == 1

RepeatedCompletionPolicy = AllCompletionPolicy

class UnstickyStickynessPolicy:
    def sticky( self ):
        return False

class StickyStickynessPolicy:
    def sticky( self ):
        return True

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
        if self.__completion.acceptsMoreCalls( self.__expectations ):
            return self.__ordering.getCurrentPossibleExpectations( self.__expectations )
        else:
            return []

    def nbRequiredCalls( self ):
        return self.__completion.nbRequiredCalls( self.__expectations )

    def getRequiredCallsExamples( self ):
        return [ "MyMock.foobar" ]

    def rewindGroups( self ):
        if self.__shallStick():
            return self
        else:
            return self.__parent.rewindGroups()

    def __shallStick( self ):
        if self.__parent is None:
            return True
        if self.__stickyness.sticky():
            return len( self.getCurrentPossibleExpectations() ) != 0
        return False

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
