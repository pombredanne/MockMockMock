PyMockMockMock is a Python [mocking][wiki_Mock] library.

[wiki_Mock]: http://en.wikipedia.org/wiki/Mock_object

Its focus is on as-strict-and-explicit-as-needed definition of the mocks'
behaviour. This allows very specific unit-tests as well as more generic
ones.

Basic usage
===========

Let's say you are writing a class that performs basic statistics on integer
numbers. This class needs some source of integers. In real execution, they
could be received from network or read from file. For your unit-tests, you
have to mock this source to simulate all kind of behaviours.

    import unittest
    from MockMockMock import Mock
    
    from MyModule import MyClass

    class MyTestCase( unittest.TestCase ):
        def setUp( self ):
            # Create the mock
            self.source = Mock( "source" )
            # Inject it in your class
            self.myInstance = MyClass( sekf.source.object )

        def tearDown( self ):
            self.source.tearDown()

        def testAverage( self ):
            self.source.expect.getNext( 3 ).andReturn( [ 42, 43, 44 ] )
            self.assertEqual( self.myInstance.average(), 43 )

        def testNoCatchExceptions( self ):
            e = TestException()
            self.source.expect.getNext( 3 ).andRaise( e )
            with self.assertRaises( TestException ) as cm:
                self.myInstance.average()
            self.assertThat( cm.exception is e )
