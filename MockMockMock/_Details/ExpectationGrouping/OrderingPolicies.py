# -*- coding: utf-8 -*-

# Copyright 2012 Vincent Jacques
# vincent@vincent-jacques.net


class OrderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
            if expectation.requiresMoreCalls():
                break
        return possible

class UnorderedOrderingPolicy:
    def getCurrentPossibleExpectations( self, expectations ):
        possible = []
        for expectation in expectations:
            possible += expectation.getCurrentPossibleExpectations()
        return possible
