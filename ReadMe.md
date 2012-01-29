PyMockMockMock is a Python
[mocking](http://en.wikipedia.org/wiki/Mock_object) library.

Its focus is on as-strict-and-explicit-as-needed definition of the mocks'
behaviour. This allows very specific unit-tests as well as more generic
ones.

Basic usage
===========

This documentation assumes you are fairly confortable with
[unittest](http://docs.python.org/library/unittest.html)

Let's say you are writing a class `Stats` that performs basic statistics on integer numbers.
This class needs some source of integers.
Using dependencies injection, you pass a `source` object to the constructor of `Stats`.
In real execution, it could read integers from keyboard or from a file.
For your unit-tests, you can mock this source to simulate all kinds of behaviours.

    import unittest
    from MockMockMock import Mock

    from Stats import Stats

    class MyTestCase( unittest.TestCase ):
        def setUp( self ):
            # Create the mock
            self.source = Mock( "source" )
            # Inject it in your class
            self.stats = Stats( self.source.object )

        def tearDown( self ):
            self.source.tearDown()

        # Test normal behaviour of your class
        def testAverage( self ):
            self.source.expect.get().andReturn( [ 42, 43, 44 ] )
            self.assertEqual( self.stats.average(), 43 )

        # Test behaviour of your class in case of exception
        def testNoCatchExceptions( self ):
            e = TestException()
            self.source.expect.get().andRaise( e )
            with self.assertRaises( TestException ) as cm:
                self.stats.average()
            self.assertThat( cm.exception is e )
