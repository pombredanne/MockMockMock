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
            mock.expect.foobar( group + "A" )
            mock.expect.foobar( group + "B" )
            makeExpectations( mock, groups[ 1: ] )
            mock.expect.foobar( group + "C" )
            mock.expect.foobar( group + "D" )

def testAllowedOrder( allowedOrder ):
    def test( self ):
        for argument in allowedOrder:
            self.call( argument )
        self.mock.tearDown()
    return test

def testForbidenOrder( forbidenOrder ):
    def test( self ):
        for argument in forbidenOrder[ : -1 ]:
            self.call( argument )
        with self.assertRaises( MockException ):
            self.call( forbidenOrder[ -1 ] )
    return test

def testTearDownError( forbidenOrder ):
    def test( self ):
        for argument in forbidenOrder:
            self.call( argument )
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

        def call( self, argument ):
            assert( len( argument ) == 2 )
            assert( argument[ 0 ] in groupMakers )
            assert( argument[ 1 ] in "ABCDX" )
            self.mock.object.foobar( argument )

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
        "uAuBuCuD",
        "uBuAuDuC",
        "uBuCuAuD",
    ],
    [
        # BaD argument
        "uAuX",
    ],
    [
        # Not completed
        "uAuBuC",
        "uAuB",
        "uA",
        "",
    ]
)

OrderedGroup = makeTestCase(
    "o",
    [
        # Completed in good order
        "oAoBoCoD",
    ],
    [
        # Wrong order
        "oB",
    ],
    [
        # Not completed
        "oAoBoC",
        "oAoB",
        "oA",
        "",
    ]
)

OptionalGroup = makeTestCase(
    "p",
    [
        # Completed in good order
        "pApBpCpD",
        # Not completed
        "pApBpC",
        "pApB",
        "pA",
        "",
    ],
    [
        # Wrong order
        "pB",
    ],
    [
    ]
)

OrderedInUnorderedGroup = makeTestCase(
    "uo",
    [
        # Original order
        "uAuBoAoBoCoDuCuD",
        # Other possible orders
        #  ordered group at once
        "oAoBoCoDuAuBuCuD",
        "uAuBuCuDoAoBoCoD",
        #  ordered group in pieces
        "oAuAoBuBoCuCoDuD",
        "oAuDoBuCoCuBoDuA",
    ],
    [
        # Ordered group in wrong order
        "uAuBoB",
    ],
    [
    ]
)

AtomicInUnorderedGroup = makeTestCase(
    "ua",
    [
        # Original order
        "uAuBaAaBaCaDuCuD",
        # Other possible orders
        #  atomic group at once
        "aAaBaCaDuAuBuCuD",
        "uAuBuCuDaAaBaCaD",
    ],
    [
        # Atomic group in wrong order
        "uAuBaB",
        # Atomic group in pieces
        "uAaAuB",
    ],
    [
    ]
)

unittest.main()
