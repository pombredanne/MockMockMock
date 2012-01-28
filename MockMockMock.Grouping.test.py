import unittest

from MockMockMock import Mock, MockException

class Ordering( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )

    def testUnorderedGroup( self ):
        with self.mock.unordered:
            self.mock.expect.foobar().andReturn( 1 )
            self.mock.expect.barbaz().andReturn( 2 )
        self.assertEqual( self.mock.object.barbaz(), 2 )
        self.assertEqual( self.mock.object.foobar(), 1 )
        self.mock.tearDown()

    def testFacultativeGroup( self ):
        self.mock.expect.foobar( 1 ).andReturn( 1 )
        with self.mock.facultative:
            self.mock.expect.foobar( 2 ).andReturn( 2 )
            self.mock.expect.foobar( 3 ).andReturn( 3 )
        self.mock.expect.foobar( 4 ).andReturn( 4 )
        self.assertEqual( self.mock.object.foobar( 1 ), 1 )
        self.assertEqual( self.mock.object.foobar( 4 ), 4 )
        self.mock.tearDown()

    def testUnorderedGroupOfSameMethod( self ):
        with self.mock.unordered:
            self.mock.expect.foobar( 1 ).andReturn( 11 )
            self.mock.expect.foobar( 1 ).andReturn( 13 )
            self.mock.expect.foobar( 2 ).andReturn( 12 )
            self.mock.expect.foobar( 1 ).andReturn( 14 )
        self.assertEqual( self.mock.object.foobar( 2 ), 12 )
        self.assertEqual( self.mock.object.foobar( 1 ), 11 )
        self.assertEqual( self.mock.object.foobar( 1 ), 13 )
        self.assertEqual( self.mock.object.foobar( 1 ), 14 )
        self.mock.tearDown()

    def testUnorderedGroupOfSamePropertyAndAnother( self ):
        with self.mock.unordered:
            self.mock.expect.foobar.andReturn( 11 )
            self.mock.expect.barbaz.andReturn( 12 )
            self.mock.expect.foobar.andReturn( 13 )
            self.mock.expect.barbaz.andReturn( 14 )
        self.assertEqual( self.mock.object.barbaz, 12 )
        self.assertEqual( self.mock.object.foobar, 11 )
        self.assertEqual( self.mock.object.barbaz, 14 )
        self.assertEqual( self.mock.object.foobar, 13 )
        self.mock.tearDown()

    def testUnorderedGroupOfSameMethodAndAnother( self ):
        with self.mock.unordered:
            self.mock.expect.foobar( 1 )
            self.mock.expect.foobar( 2 )
            self.mock.expect.barbaz()
        self.mock.object.foobar( 2 )
        self.mock.object.barbaz()
        self.mock.object.foobar( 1 )
        self.mock.tearDown()

    ### @todo Allow unordered property and method calls on the same name: difficult
    def testUnorderedGroupOfSameMethodAndProperty( self ):
        with self.assertRaises( MockException ) as cm:
            with self.mock.unordered:
                self.mock.expect.foobar()
                self.mock.expect.foobar
            self.mock.object.foobar
            self.mock.object.foobar()
        self.assertEqual( cm.exception.message, "MyMock.foobar is expected as a property and as a method call in an unordered group" )

    def testUnorderedGroupOfSamePropertyAndMethod( self ):
        with self.assertRaises( MockException ) as cm:
            with self.mock.unordered:
                self.mock.expect.foobar
                self.mock.expect.foobar()
            self.mock.object.foobar()
            self.mock.object.foobar
        self.assertEqual( cm.exception.message, "MyMock.foobar is expected as a property and as a method call in an unordered group" )

class OrderedGroupInUnordered( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.mock = Mock( "MyMock" )
        with self.mock.unordered:
            self.mock.expect.u1()
            with self.mock.ordered:
                self.mock.expect.u2o1()
                self.mock.expect.u2o2()
                self.mock.expect.u2o3()
            self.mock.expect.u3()

    def testAllowedOrders( self ):
        for ordering in [
            ### Comments about enumeration of all allowed orderings
            # 21 called first => 22 and 23 called near 1 and 3
            #   1 called before 3
            [ 21, 22, 23, 1, 3 ], [ 21, 22, 1, 23, 3 ], [ 21, 22, 1, 3, 23 ],
            [ 21, 1, 22, 23, 3 ], [ 21, 1, 22, 3, 23 ], [ 21, 1, 3, 22, 23 ],
            #   1 called after 3
            [ 21, 22, 23, 3, 1 ], [ 21, 22, 3, 23, 1 ], [ 21, 22, 3, 1, 23 ],
            [ 21, 3, 22, 23, 1 ], [ 21, 3, 22, 1, 23 ], [ 21, 3, 1, 22, 23 ],
            # 21 called second
            #   1 called before 3 => 22 and 23 called near 3
            [ 1, 21, 22, 23, 3 ], [ 1, 21, 22, 3, 23 ], [ 1, 21, 3, 22, 23 ],
            #   1 called after 3 => 22 and 23 called near 1
            [ 3, 21, 22, 23, 1 ], [ 3, 21, 22, 1, 23 ], [ 3, 21, 1, 22, 23 ],
            # 21 called third => 22 and 23 called just after 21
            [ 1, 3, 21, 22, 23 ], [ 3, 1, 21, 22, 23 ]
        ] :
            self.setUp()
            for m in ordering:
                if m == 1: self.mock.object.u1()
                if m == 21: self.mock.object.u2o1()
                if m == 22: self.mock.object.u2o2()
                if m == 23: self.mock.object.u2o3()
                if m == 3: self.mock.object.u3()
            self.mock.tearDown()

    def testForbidenOrder( self ):
        self.mock.object.u3()
        self.mock.object.u2o1()
        with self.assertRaises( MockException ) as cm:
            self.mock.object.u2o3()
        self.assertEqual( cm.exception.message, "MyMock.u2o3 called instead of MyMock.u1 or MyMock.u2o2" )

unittest.main()
