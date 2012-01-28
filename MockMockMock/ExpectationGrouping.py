class OrderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
            if len( expectation.requiredCalls() ) > 0:
                break
        return possible

class UnorderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
        return possible

class AllCompletionPolicy:
    def requiredCalls( self, expectations ):
        required = []
        for expectation in expectations:
            required += expectation.requiredCalls()
        return required

class UnstickyStickynessPolicy:
    pass

class ExpectationGroup:
    def __init__( self, ordering, completion, stickyness ):
        self.__ordering = ordering
        self.__completion = completion
        self.__stickyness = stickyness
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__ordering.getCurrentPossibleExpectations( self.__expectations )

    def removeExpectation( self, expectation ):
        if expectation in self.__expectations:
            self.__expectations.remove( expectation )
        else:
            for e in self.__expectations:
                if e.removeExpectation( expectation ):
                    self.__expectations.remove( e )
                    break
        return len( self.__expectations ) == 0

    def requiredCalls( self ):
        return self.__completion.requiredCalls( self.__expectations )

def makeGroup( ordering, completion, stickyness ):
    class Group( ExpectationGroup ):
        def __init__( self ):
            ExpectationGroup.__init__( self, ordering(), completion(), stickyness() )

    return Group

OrderedExpectationGroup = makeGroup( OrderedOrderingPolicy, AllCompletionPolicy, UnstickyStickynessPolicy )
UnorderedExpectationGroup = makeGroup( UnorderedOrderingPolicy, AllCompletionPolicy, UnstickyStickynessPolicy )
