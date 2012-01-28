class OrderedExpectationGroup:
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        possible = []
        for expectation in self.__expectations:
            possible += expectation.getCurrentPossibleExpectations()
            if len( expectation.requiredCalls() ) > 0:
                break
        return possible

    def removeExpectation( self, expectation ):
        if expectation is self.__expectations[ 0 ]:
            self.__expectations = self.__expectations[ 1 : ]
        else:
            if self.__expectations[ 0 ].removeExpectation( expectation ):
                self.__expectations = self.__expectations[ 1 : ]
        return len( self.__expectations ) == 0

    def requiredCalls( self ):
        required = []
        for expectation in self.__expectations:
            required += expectation.requiredCalls()
        return required

class UnorderedExpectationGroup:
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        possible = []
        for expectation in self.__expectations:
            possible += expectation.getCurrentPossibleExpectations()
        return possible

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
        required = []
        for expectation in self.__expectations:
            required += expectation.requiredCalls()
        return required

class FacultativeExpectationGroup:
    def __init__( self ):
        self.__expectations = []

    def addExpectation( self, expectation ):
        self.__expectations.append( expectation )

    def getCurrentPossibleExpectations( self ):
        return self.__expectations[ 0 ].getCurrentPossibleExpectations()

    def removeExpectation( self, expectation ):
        if expectation is self.__expectations[ 0 ]:
            self.__expectations = self.__expectations[ 1 : ]
        else:
            if self.__expectations[ 0 ].removeExpectation( expectation ):
                self.__expectations = self.__expectations[ 1 : ]
        return len( self.__expectations ) == 0

    def requiredCalls( self ):
        return []
