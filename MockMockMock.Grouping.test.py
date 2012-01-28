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
            mock.expect.foobar( "a" + group )
            mock.expect.foobar( "b" + group )
            makeExpectations( mock, groups[ 1: ] )
            mock.expect.foobar( "c" + group )
            mock.expect.foobar( "d" + group )

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
        "aubucudu",
        "buauducu",
        "bucuaudu",
    ],
    [
        # Not completed
        "aubucu",
        "aubu",
        "au",
        "",
        # Bad argument
        "auxx" ,
    ]
)

OrderedGroup = makeTestCase(
    "o",
    [
        # Completed in good order
        "aobocodo",
    ],
    [
        # Not completed
        "aoboco",
        "aobo",
        "ao",
        "",
        # Wrong order
        "boaodoco",
    ]
)

OrderedInUnorderedGroup = makeTestCase(
    "uo",
    [
        # Original order
        "aubuaobocodocudu",
        # Other possible orders
        "aobocodoaubucudu",
        "aoaubobucocudodu",
    ],
    [
        "aububoaocodocudu",
    ]
)

unittest.main()
