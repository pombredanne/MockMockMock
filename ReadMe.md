3 threads: thread 1 appelle A, thread 2 appelle B1 puis B2 puis B3, thread 3 appelle C
Le mock doit accepter tout ordonancement, y compris B1 A B2 C B3. Donc un ordered dans
un unordered peut être appelé en plusieurs fois.

Une fonction qui doit faire soit A1, A2, B1, B2, soit B1, B2, A1, A2: le mock doit refuser
A1, B1, A2, B2 donc un unordered composé de 2 ordered ne convient pas. Donc il faut un atomic
et faire un unordered contenant deux atomic.

----------------------------------------------------------
# Expect facultative calls
# Expect repetitions of calls
# Test groups in groups in groups in...

# Allow other arguments checking than simple constants
# Maybe mock.expect.foobar.withArguments( 42 ) could be a synonym for mock.expect.foobar( 42 ) and we could add a withArgumentsChecker to handle more complex cases
# Transmit arguments to andExecute's callable (usefull when repeated, or with other arguments checkers): mock.expect.foobar( 12 ).andExecute( lambda n : n + 1 ).repeated( 5 )
# Allow positional arguments (*args) to be passed by name (**kwds)

# Check that expected properties do not allow call and that expected method calls require call

# Derive a class from unittest.TestCase that provides a mock factory and auto-tearDowns the created mocks

# Be thread safe
----------------------------------------------------------

Policies defining a Group:
 - ordering: called to know which calls are possible (returns a collection of Expectations)
    - Ordered: componants must be call in same order as they were expected
    - Unordered: componants can be called in any order
 - completion: called to know if the group expects more calls (returns an int) or accepts more calls (returns a bool)
    - All: all componants must be called
    - Exactly( n ): exactly n componants must be called
    - AtLeast( n ): at least n componants must be called
    - AtMostAllMinus( n ): at most all but n componants can be called
    - Any: AtLeast( 0 )
    - Repeated: 
 - stickyness: called to know if next call can be search in parent group (returns a bool)
    - Sticky: next call must be in same group
    - Unsticky: next call can be in parent group

ordered = Ordered, All, Unsticky
unordered = Unordered, All, Unsticky
atomic = Ordered, All, Sticky
optional = Ordered, Any, Unsticky
alternative = Unordered, Exactly( 1 ), Unsticky
repeated = Ordered, Repeated, Unsticky
