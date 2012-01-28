import unittest

from MockMockMock import Mock, MockException

groupMakers = {
    "o" : lambda m: m.ordered,
    "u" : lambda m: m.unordered,
    "a" : lambda m: m.atomic,
    "p" : lambda m: m.optional,
    "l" : lambda m: m.alternative,
    "r" : lambda m: m.repeated,
}

def makeExpectations( mock, groups ):
    if len( groups ) > 0:
        group = groups[ 0 ]
        with groupMakers[ group ]( mock ):
            mock.expect.foobar( group + "a" )
            mock.expect.foobar( group + "b" )
            makeExpectations( mock, groups[ 1: ] )
            mock.expect.foobar( group + "c" )
            mock.expect.foobar( group + "d" )

def makeTestCase( groups, allowedOrders, forbidenOrders ):
    groups = list( groups )
    allowedOrders = [
        [
            allowedOrder[ 2 * i : 2 * i + 2 ]
            for i in range( len( allowedOrder ) / 2 )
        ]
        for allowedOrder in allowedOrders
    ]
    forbidenOrders = [
        [
            forbidenOrder[ 2 * i : 2 * i + 2 ]
            for i in range( len( forbidenOrder ) / 2 )
        ]
        for forbidenOrder in forbidenOrders
    ]

    class TestCase( unittest.TestCase ):
        def setUp( self ):
            unittest.TestCase.setUp( self )
            self.mock = Mock( "MyMock" )
            makeExpectations( self.mock, groups )

    for allowedOrder in allowedOrders:
        def test( self ):
            for argument in allowedOrder:
                self.mock.object.foobar( argument )
            self.mock.tearDown()

        setattr( TestCase, "test_" + "".join( allowedOrder ), test )

    for forbidenOrder in forbidenOrders:
        def test( self ):
            with self.assertRaises( MockException ):
                for argument in forbidenOrder:
                    self.mock.object.foobar( argument )
                self.mock.tearDown()

        setattr( TestCase, "test_" + "".join( forbidenOrder ), test )

    TestCase.__name__ = "TestCase_" + "".join( groups )
        
    return TestCase
    
UnorderedGroup = makeTestCase(
    "u",
    [
        # Completed in any order
        "uaubucud",
        "ubuauduc",
        "ubucuaud",
    ],
    [
        # Not completed
        "uaubuc",
        "uaub",
        "ua",
        "",
        # Bad argument
        "uaxx" ,
    ]
)

OrderedGroup = makeTestCase(
    "o",
    [
        # Completed in good order
        "oaobocod",
    ],
    [
        # Not completed
        "oaoboc",
        "oaob",
        "oa",
        "",
        # Wrong order
        "oboaodoc",
    ]
)

OrderedInUnorderedGroup = makeTestCase(
    "uo",
    [
        # Original order
        "uauboaobocoducud",
        # Other possible orders
        #  ordered group at once
        "oaobocoduaubucud",
        "uaubucudoaobocod",
        #  ordered group in pieces
        "oauaobubocucodud",
        "oaudobucocubodua",
    ],
    [
        # Ordered group in wroing order
        "uauboboaocoducud",
    ]
)

unittest.main()
