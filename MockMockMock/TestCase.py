import unittest

from Factory import Factory

class TestCase( unittest.TestCase ):
    def setUp( self ):
        unittest.TestCase.setUp( self )
        self.__factory = Factory()

    def tearDown( self ):
        self.__factory.tearDown()

    def createMock( self, name ):
        return self.__factory.create( name )
