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

def testAllowedOrder( allowedOrder ):
    def test( self ):
        for argument in allowedOrder:
            self.mock.object.foobar( argument )
        self.mock.tearDown()
    return test

def testForbidenOrder( forbidenOrder ):
    def test( self ):
        for argument in forbidenOrder[ : -1 ]:
            self.mock.object.foobar( argument )
        with self.assertRaises( MockException ):
                self.mock.object.foobar( forbidenOrder[ -1 ] )
    return test

def testTearDownError( forbidenOrder ):
    def test( self ):
        for argument in forbidenOrder:
            self.mock.object.foobar( argument )
        with self.assertRaises( MockException ):
            self.mock.tearDown()
    return test

def makeTestCase( groups, allowedOrders, forbidenOrders, tearDownErrors ):
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
    tearDownErrors = [
        [
            tearDownError[ 2 * i : 2 * i + 2 ]
            for i in range( len( tearDownError ) / 2 )
        ]
        for tearDownError in tearDownErrors
    ]

    class TestCase( unittest.TestCase ):
        def setUp( self ):
            unittest.TestCase.setUp( self )
            self.mock = Mock( "MyMock" )
            makeExpectations( self.mock, groups )

    for allowedOrder in allowedOrders:
        setattr( TestCase, "test_" + "".join( allowedOrder ), testAllowedOrder( allowedOrder ) )

    for forbidenOrder in forbidenOrders:
        setattr( TestCase, "test_" + "".join( forbidenOrder ), testForbidenOrder( forbidenOrder ) )

    for tearDownError in tearDownErrors:
        setattr( TestCase, "test_" + "".join( tearDownError ), testTearDownError( tearDownError ) )

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
        # Bad argument
        "uaxx",
    ],
    [
        # Not completed
        "uaubuc",
        "uaub",
        "ua",
        "",
    ]
)

OrderedGroup = makeTestCase(
    "o",
    [
        # Completed in good order
        "oaobocod",
    ],
    [
        # Wrong order
        "ob",
    ],
    [
        # Not completed
        "oaoboc",
        "oaob",
        "oa",
        "",
    ]
)

OptionalGroup = makeTestCase(
    "p",
    [
        # Completed in good order
        "papbpcpd",
        # Not completed
        "papbpc",
        "papb",
        "pa",
        "",
    ],
    [
        # Wrong order
        "pb",
    ],
    [
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
        # Ordered group in wrong order
        "uaubob",
    ],
    [
    ]
)

# AtomicInUnorderedGroup = makeTestCase(
    # "ua",
    # [
        # # Original order
        # "uaubaaabacaducud",
        # # Other possible orders
        # #  atomic group at once
        # "aaabacaduaubucud",
        # "uaubucudaaabacad",
    # ],
    # [
        # # Atomic group in wrong order
        # "uaubabaaacaducud",
        # # Atomic group in pieces
        # "aauaabubacucadud",
        # "aaudabucacubadua",
    # ],
    # [
    # ]
# )

unittest.main()
