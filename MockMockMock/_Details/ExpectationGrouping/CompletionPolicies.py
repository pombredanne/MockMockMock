# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net


class AllCompletionPolicy:
    def requiresMoreCalls( self, expectations ):
        for expectation in expectations:
            if expectation.requiresMoreCalls():
                return True
        return False

    def getRequiredCallsExamples( self, expectations ):
        required = []
        for expectation in expectations:
            if expectation.requiresMoreCalls():
                required += expectation.getRequiredCallsExamples()
        return required

    def acceptsMoreCalls( self, expectations ):
        return any( len(expectation.getCurrentPossibleExpectations() ) != 0 for expectation in expectations )

    def markExpectationCalled( self, expectations, expectation ):
        pass

class AnyCompletionPolicy:
    def requiresMoreCalls( self, expectations ):
        return False

    def acceptsMoreCalls( self, expectations ):
        return True

    def markExpectationCalled( self, expectations, expectation ):
        pass

class ExactlyOneCompletionPolicy:
    def requiresMoreCalls( self, expectations ):
        for expectation in expectations:
            if not expectation.requiresMoreCalls():
                return False
        return True

    def getRequiredCallsExamples( self, expectations ):
        return []

    def acceptsMoreCalls( self, expectations ):
        return self.requiresMoreCalls( expectations )

    def markExpectationCalled( self, expectations, expectation ):
        pass

class RepeatedCompletionPolicy:
    def requiresMoreCalls( self, expectations ):
        required = 0
        if expectations[ 0 ].called:
            for expectation in expectations:
                required += expectation.requiresMoreCalls()
        return required

    def getRequiredCallsExamples( self, expectations ):
        return []

    def acceptsMoreCalls( self, expectations ):
        return True

    def markExpectationCalled( self, expectations, expectation ):
        if expectation is expectations[ -1 ]:
            for e in expectations:
                e.resetCall()
