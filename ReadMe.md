PyMockMockMock is a Python
[mocking](http://en.wikipedia.org/wiki/Mock_object) library.

It focuses on very explicit definition of the mocks' behaviour.
It allows as-specific-as-needed unit-tests as well as more generic ones.

Basic usage
===========

This documentation assumes you are fairly confortable with
[unittest](http://docs.python.org/library/unittest.html)

Let's say you are writing a class `Stats` that performs basic statistics on integer numbers.
This class needs some source of integers.
Using dependency injection, you pass a `source` object to the constructor of `Stats`.
In real execution, it could read integers from keyboard or from a file.
For your unit-tests, you can mock this source to simulate all kinds of behaviours.

So, here is how you would do that with PyMockMockMock. Create a test case:

    import unittest
    from MockMockMock import Mock

    from Stats import Stats

    class MyTestCase( unittest.TestCase ):
        def setUp( self ):

In `setUp`, you create the mock...

            self.source = Mock( "source" )

... and inject it in your constructor:

            self.stats = Stats( self.source.object )

In `tearDown`, you check that each mock has been used correctly:

        def tearDown( self ):
            self.source.tearDown()

Then, in you test methods, there are two phases. First, instruct the mock about how to behave...

        def testAverage( self ):
            self.source.expect.get().andReturn( [ 42, 43, 44 ] )

... then call your code, that will call the mock.

            self.assertEqual( self.stats.average(), 43 )

This way, you:

- are checking that your code calls what it has to call (the final call to Mock.tearDown will detect if some call was `expect`ed, but not called)
- can inject to your code wathever behaviour you want to test.

Of course, do not forget to actually run the tests:

    unittest.main()

Mock behaviour
==============

Expectations
------------

You can instruct the mock to expect successive calls:

        def testXxxx( self ):
            self.source.expect.get().andReturn( [ 1, 2, 3, 4 ] )
            self.source.expect.isFinished().andReturn( True )

            self.assertEqual( self.stats.average(), 2.5 )

You can expect successive calls to the same method and have different behaviour each time:

        def testXxxx( self ):
            self.source.expect.get().andReturn( [ 1, 2, 3, 4 ] )
            self.source.expect.get().andReturn( [ 5, 6, 7 ] )
            self.source.expect.get().andReturn( [] )

            self.assertEqual( self.stats.average(), 4 )

You can expect arguments in method calls:

        def testXxxx( self ):
            self.source.expect.get( 5 ).andReturn( [ 1, 2, 3, 4, 5 ] )

            self.assertEqual( self.stats.average(), 3 )

You can expect calls to properties as well:

        def testXxxx( self ):
            self.source.expect.name.andReturn( "Mock" )

            self.assertEqual( self.stats.getSourceName(), "Mock" )

Behaviour
---------

You can simulate a source that raises exceptions:

        def testXxxx( self ):
            self.source.expect.get().andRaise( Exception() )

            self.assertRaises( Exception, self.stats.average )

Mock grouping
=============

By default, all `expect`ed calls are registered in an `ordered` group.
This means that the mock will raise a `MockException` if your code does not call those methods in the order they were `expect`ed.
The `Mock.tearDown` method will raise `MockException` as if your code does not call all the `expect`ed methods.

To tweak this behaviour, there are several other available grouping methods.

You can tell the mock to expect all calls, but in any order:

        def testXxxx( self ):
            with self.source.unordered:
                self.source.expect.foobar()
                self.source.expect.barbaz()

            self.stats.frobnicate()

You can tell the mock that some calls are optional:

        def testXxxx( self ):
            with self.source.optional:
                self.source.expect.foobar()
                self.source.expect.barbaz()

            self.stats.frobnicate()
