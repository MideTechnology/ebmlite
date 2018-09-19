import unittest
import core
import os, sys
import numpy as np
from datetime import datetime, timedelta

from core     import *
from decoding import *
from encoding import *
from mock     import *
from numpy    import inf
from util     import *


    
class MockStream(object):
    def __init__(self):
        self.string = ''
        self.position = 0
    
    def read(self, n=None):
        if n is None:
            n = len(self.string) - self.position
        retVal = self.string[self.position:self.position+n]
        self.position += n
        return retVal
    
    def seek(self, offset, whence=0):
        if whence == 0:
            self.position = offset
        elif whence == 1:
            self.position += offset
        else:
            self.position = len(self.string) + offset
        
        return self.position 
        
    def tell(self):
        return self.position
        
        
                            
class testCoreElement(unittest.TestCase):
    
    
    
    def setUp(self):        
        
        self.mockStream = MockStream()
        
        # set element as:
        #       id:   00 1111  0101 0110
        #    value:   11 0001  1110 1010
        #   header: 0100 1111  0101 0110
        #     data: 0111 0001  1110 1010
        self.mockStream.string = '\x4f\x56\x71\xea'
        
        self.element = Element(stream=self.mockStream, offset=0, size=4, \
                               payloadOffset=2)
        
        
    
    def testParse(self):
        """ Test parsing a generic element as a bytestring. """
        
        self.assertEqual(self.element.parse(self.mockStream, 4), '\x4f\x56\x71\xea')
    
    
    
    def testValue(self):
        """ Test getting a value from a generic element as a bytestring. """
        
        # Test first parse
        self.assertEqual(self.element.value, '\x71\xea')
        
        # Test that mockstring is empty and that the value has been cached
        self.assertEqual(self.mockStream.position, 6)
        self.assertEqual(self.element.value, '\x71\xea')
    
    
    
    def testGetRaw(self):
        """ Test getting a raw bytestring of a full generic element. """
        
        self.assertEqual(self.element.getRaw(), '\x4f\x56\x71\xea')
                             
    
    
    def testGetRawValue(self):
        """ Test getting a raw bytestring of the data from a generic element. """
        
        self.assertEqual(self.element.getRawValue(), '\x71\xea')
    
    
    
    def testGc(self):
        """ Test clearing caches. """
        
        self.assertEqual(self.element._value, None)
        self.assertEqual(self.element.gc(), 0)
        
        self.element.value
        self.assertEqual(self.element._value, '\x71\xea')
        
        self.assertEqual(self.element.gc(), 1)
        self.assertEqual(self.element._value, None)
    
    
    
    def testEncodePayload(self):
        """ Test encoding a payload. """
        
        self.assertEqual(self.element.encodePayload('\x4f\x56\x71\xea', length=4), \
                         '\x4f\x56\x71\xea')

    
    
    def testEncode(self):
        """ Test encoding a full EBML element. """
        
        # TODO figure out why this isn't cooperating
        # self.assertEqual(self.element.encode('\x71\xea', 2), '\x71\xea')
        pass
    
    
    
    def testDump(self):
        """Test dumping an element to a dict"""
        
        self.assertEqual(self.element.dump(), '\x71\xea')
        
        
        
class testIntElements(unittest.TestCase):
    
    
    
    def setUp(self):
                
        self.mockStream = MockStream()
        
        # -1000 = -0b0000 0011  1110 1000 =>
        # 0b1111 1100  0001 1000 =>
        # 0xfc18
        self.mockStream.string = '\xfc\x18'
                
        self.intEl1 = IntegerElement(stream=self.mockStream, offset=0, size=4, \
                                     payloadOffset=2)
        self.intEl1.id = 0x7c        
        self.intEl1.schema = 'mide.xml'
        
        self.uintEl1 = UIntegerElement(stream=self.mockStream, offset=0, size=4, 
                                       payloadOffset=2)

    
    
    def testIntParse(self):
        self.assertEqual(self.intEl1.parse(self.mockStream, 2), -1000) 
    
    
    
    def testIntEncode(self):
        self.assertEqual(self.intEl1.encodePayload(0x4242, 2), 'BB')
        self.assertEqual(self.intEl1.encodePayload(-1000, 2), '\xfc\x18')
    
    
    
    def testIntEq(self):
        
        m1 = MockStream()
        m2 = MockStream()
        
        self.mockStream.string = '\x4f\x56\x71\xea'
        m1.string = 'abcd'
        m2.string = self.mockStream.string
        
        intEl2 = IntegerElement(stream=m1, offset=0, size=4, payloadOffset=2)
        intEl2.id = 0x7c
        intEl2.schema = 'mide.xml'
        
        intEl3 = IntegerElement(stream=m2, offset=0, size=4, payloadOffset=2)
        intEl3.id = 0x7c
        intEl3.schema = 'mide.xml'
                
        self.assertFalse(self.intEl1 == intEl2)
        
        self.mockStream.string = '\x4f\x56\x71\xea'
        
        self.assertEqual(self.intEl1, intEl3)
        
                
    
    def testUIntParse(self):
        self.assertEqual(self.uintEl1.parse(self.mockStream, 2), 64536)
    
    
    
    def testUintEncode(self):
        self.assertEqual(self.uintEl1.encodePayload(0x4142), 'AB')
        


class testFloatElements(unittest.TestCase):
    
    
    
    def setUp(self):
                
        self.mockStream = MockStream()
        
        # -1000 = -0b0000 0011  1110 1000 =>
        # 0b1111 1100  0001 1000 =>
        # 0xfc18
        self.mockStream.string = '\x4f\x56\x3e\xaa\xaa\xab'
                
        self.floatEl = FloatElement(stream=self.mockStream, offset=0, size=4, \
                                     payloadOffset=2)
        self.floatEl.id = 0x7c        
        self.floatEl.schema = 'mide.xml'
    
    
    
    def testFloatEq(self):
        self.assertEqual(self.floatEl.value, np.float32(1.0/3.0))
    
    
    
    def testFloatParse(self):
        self.mockStream.seek(2)
        self.assertEqual(self.floatEl.parse(self.mockStream, 4), np.float32(1.0/3.0))
    
    
    
    def testFloatEncode(self):
        self.assertEqual(self.floatEl.encodePayload(1.0/3.0, length=4), \
                         '\x3e\xaa\xaa\xab')
        


class testStringElements(unittest.TestCase):
    
    
    
    def setUp(self):
                
        self.mockStream = MockStream()
        
        # -1000 = -0b0000 0011  1110 1000 =>
        # 0b1111 1100  0001 1000 =>
        # 0xfc18
        self.mockStream.string = '\x4f\x40bork\x4f\x40bork'
                
        self.strEl1 = StringElement(stream=self.mockStream, offset=0, size=4, \
                                     payloadOffset=2)
        self.strEl1.id = 0x7c        
        self.strEl1.schema = 'mide.xml'
                
        self.strEl2 = StringElement(stream=self.mockStream, offset=0, size=4, \
                                     payloadOffset=2)
        self.strEl2.id = 0x7c        
        self.strEl2.schema = 'mide.xml'
                
        self.strEl3 = StringElement(stream=self.mockStream, offset=0, size=8, \
                                     payloadOffset=2)
        self.strEl3.id = 0x5e        
        self.strEl3.schema = 'matroska.xml'
        
        self.uniEl = UnicodeElement(stream=self.mockStream, offset=0, size=4, \
                                    payloadOffset=2)
    
    
    
    def testStringEq(self):
        self.assertEqual(self.strEl1, self.strEl2)
        self.assertNotEqual(self.strEl2, self.strEl3)
    
    
    
    def testStringLen(self):
        self.assertEqual(len(self.strEl1), 4)
        self.assertEqual(len(self.strEl3), 8)
    
    
    
    def testStringParse(self):
        self.mockStream.seek(2)
        self.assertEqual(self.strEl1.parse(self.mockStream, 4), 'bork')
    
    
    
    def testStringEncode(self):
        self.assertEqual(self.strEl1.encodePayload('bork'), 'bork')
    
    
    
    def testUnicodeLen(self):
        self.assertEqual(len(self.uniEl), 4)
    
    
    
    def testUnicodeParse(self):
        self.mockStream.seek(2)
        self.assertEqual(self.uniEl.parse(self.mockStream, 4), u'bork')
    
    
    
    def testUnicodeEncode(self):
        self.assertEqual(self.strEl1.encodePayload('bork'), u'bork')
        
        
        
class testDataElements(unittest.TestCase):
    
    
    
    def setUp(self):
                
        self.mockStream = MockStream()
        
        self.mockStream.string = '\x80\x07\x71\xe1\x58\x4d\x0f\x00\x00'
        
        self.datEl = DateElement(stream=self.mockStream, offset=1, size=8, \
                                 payloadOffset=1)
    
    
    
    def testDateParse(self):
        self.mockStream.seek(1)
        self.assertEqual(self.datEl.parse(self.mockStream, 8), \
                         datetime.datetime(2018, 1, 1))
    
    
    
    def testDateEncode(self):
        self.assertEqual(self.datEl.encodePayload(datetime.datetime(2018, 1, 1)), \
                         '\x07\x71\xe1\x58\x4d\x0f\x00\x00')
    
    

class testBinaryElements(unittest.TestCase):
    
    
    
    def setUp(self):
        self.binEl = BinaryElement(MockStream(), size=2)
    
    
    
    def testBinaryLen(self):
        self.assertEqual(len(self.binEl), 2)
    
    
    
class testVoidElements(unittest.TestCase):
    
    
    
    def setUp(self):
                
        self.mockStream = MockStream()
        
        # -1000 = -0b0000 0011  1110 1000 =>
        # 0b1111 1100  0001 1000 =>
        # 0xfc18
        self.mockStream.string = '\x00\x00\x00A'
                
        self.voiEl = VoidElement(stream=self.mockStream, offset=1, size=4, \
                                     payloadOffset=1)
        self.voiEl.id = 0x7c        
        self.voiEl.schema = 'mide.xml'
    
    
    
    def testVoidParse(self):
        self.assertEqual(self.voiEl.parse(self.mockStream, 4), bytearray())
    
    
    
    def testVoidEncode(self):
        self.assertEqual(self.voiEl.encodePayload(0x41424344, length=4), \
                         '\xff\xff\xff\xff')
    
    
    
class testUnknownElements(unittest.TestCase):
    
    
    
    def setUp(self):
                
        self.mockStream = MockStream()
        
        # -1000 = -0b0000 0011  1110 1000 =>
        # 0b1111 1100  0001 1000 =>
        # 0xfc18
        self.mockStream.string = '\x00\x00\x00A'
                
        self.unkEl1 = VoidElement(stream=self.mockStream, offset=1, size=4, \
                                     payloadOffset=1)
        self.unkEl1.id = 0x7c        
        self.unkEl1.schema = 'mide.xml'
                
        self.unkEl2 = VoidElement(stream=self.mockStream, offset=1, size=4, \
                                     payloadOffset=1)
        self.unkEl2.id = 0x7c        
        self.unkEl2.schema = 'mide.xml'
                
        self.unkEl3 = VoidElement(stream=self.mockStream, offset=1, size=4, \
                                     payloadOffset=1)
        self.unkEl3.id = 0x7d       
        self.unkEl3.schema = 'mide.xml'
    
    
    
    def testUnknownEq(self):
        self.assertEqual(self.unkEl1, self.unkEl2)
        self.assertNotEqual(self.unkEl1, self.unkEl3)
        
        
        
class testMasterElements(unittest.TestCase):
    
    
    
    def setUp(self):
                
        self.mockStream = MockStream()
        """ Master Element:   ID: 0x1A45DFA3
                            Size: 0x84
                           Value:
                UInt Element:   ID: 0x4286
                              Size: 0x81
                             value: 0x42 
        """
        self.mockStream.string = '\x1A\x45\xDF\xA3\x84\x42\x86\x81\x10'
        
        self.element = MasterElement(stream=self.mockStream, \
                                     offset=0, \
                                     size=4, \
                                     payloadOffset=5)
        self.element.schema = loadSchema('.\\schemata\\mide.xml')
        self.element.id = 0x1A45DFA3
    
    
    
    def testParse(self):
        masterEl = MasterElement()
        masterEl.id = 0x1A45DFA3
        masterEl.size = 4
        masterEl.schema = loadSchema('.\\schemata\\mide.xml')
        self.assertEqual(masterEl, self.element)
        
        sEbmlVer = self.element.parse()[0]
        sEbmlVer.stream = self.mockStream
        ebmlVer = masterEl.schema.elements[0x4286](masterEl.stream, 5, 1, 8)
        ebmlVer.stream = self.mockStream        
        ebmlVer._value = 16
        sEbmlVer == ebmlVer
        self.assertEqual(sEbmlVer, ebmlVer)
    
    
    
    def testParseElement(self):        
        self.mockStream.seek(5)
        newVer = self.element.parseElement(self.mockStream)[0]
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        
        self.assertEqual(newVer, ebmlVer)
    
    
    
    def testIter(self):
        self.mockStream.seek(5)
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        
        self.assertEqual(list(self.element), [ebmlVer])
    
    
    
    def testLen(self):
        self.assertEqual(len(self.element), 0)
    
    
    
    def testValue(self):
        self.mockStream.seek(5)
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        self.assertEqual(self.element.value, [ebmlVer])
    
    
    
    def testGetItem(self):
        self.mockStream.seek(5)
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        self.assertEqual(self.element[0], ebmlVer)
    
    
    
    def testGc(self):
        self.assertIsNone(self.element._value)
        
        self.element.value
        self.assertIsNotNone(self.element._value)
        
        self.element.gc()
        self.assertIsNone(self.element._value)
    
    
    
    def testEncodePayload(self):
        print self.element.encodePayload({0x4286:16})
        pass
    
    
    
    def testEncode(self):
        pass
    
    
    
    def testDump(self):
        pass
        
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()