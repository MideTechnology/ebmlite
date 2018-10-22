import collections
import datetime
import types
import unittest
from StringIO import StringIO

from core import loadSchema, BinaryElement, DateElement, Element, FloatElement, \
        IntegerElement, MasterElement, StringElement, UIntegerElement, \
        UnicodeElement, VoidElement

           
                            
class testCoreElement(unittest.TestCase):
    """ Unit tests for ebmlite.core.Element """
    
    
    
    def setUp(self):
        """ Set up the unit tests with a generic Element class with some
            custom data (id: 0x4F56, value: 0x71EA).
        """
        
        # set element as:
        #       id:   00 1111  0101 0110
        #    value:   11 0001  1110 1010
        #   header: 0100 1111  0101 0110
        #     data: 0111 0001  1110 1010
        self.mockStream = StringIO('\x4f\x56\x71\xea')
        
        GenericElement = type('GenericElement', (Element,),
                              {'id':0x4343, 'name':'Generic Element',
                               'schema':loadSchema('./schemata/mide.xml'),
                               'mandatory':False, 'multiple':False,
                               'precache':False, 'length':4, 'children':dict(),
                               '__doc__':'no'})
        
        self.element = GenericElement(stream=self.mockStream, offset=0, size=4,
                               payloadOffset=2)
        
        
    
    def testParse(self):
        """ Test parsing a generic element as a bytestring. """
        
        self.assertEqual(self.element.parse(self.mockStream, 4), '\x4f\x56\x71\xea')
    
    
    
    def testValue(self):
        """ Test getting a value from a generic element as a bytestring. """
        
        # Test first parse
        self.assertEqual(self.element.value, '\x71\xea')
        
        # Test that mockstring is empty and that the value has been cached
        self.assertEqual(self.mockStream.pos, 4)
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
        
        self.assertEqual(self.element.encodePayload('\x4f\x56\x71\xea', length=4),
                         '\x4f\x56\x71\xea')

    
    
    def testEncode(self):
        """ Test encoding a full EBML element. """

        self.assertEqual(self.element.encode('\x71\xea', 2), 'CC\x82\x71\xea')
        pass
    
    
    
    def testDump(self):
        """Test dumping an element to a dict"""
        
        self.assertEqual(self.element.dump(), '\x71\xea')
        
        
        
class testIntElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.IntElement """
    
    
    
    def setUp(self):
        """ Set up the unit tests with an IntegerElement class with some
            custom data (id: -, value: 0xFC18).
        """
        
        # -1000 = -0b0000 0011  1110 1000 =>
        # 0b1111 1100  0001 1000 =>
        # 0xfc18
        self.mockStream = StringIO('\xfc\x18')
                
        self.intEl1 = IntegerElement(stream=self.mockStream, offset=0, size=4,
                                     payloadOffset=2)
        self.intEl1.id = 0x7c        
        self.intEl1.schema = 'mide.xml'
        
        self.uintEl1 = UIntegerElement(stream=self.mockStream, offset=0, size=4,
                                       payloadOffset=2)

    
    
    def testIntParse(self):
        """ Test parsing an IntegerElement. """

        self.assertEqual(self.intEl1.parse(self.mockStream, 2), -1000) 
    
    
    
    def testIntEncode(self):
        """ Test encoding an IntegerElement. """

        self.assertEqual(self.intEl1.encodePayload(0x4242, 2), 'BB')
        self.assertEqual(self.intEl1.encodePayload(-1000, 2), '\xfc\x18')
    
    
    
    def testIntEq(self):
        """ Test equality of IntegerElements. """

        # Define buffers for IntegerElements
        m1 = StringIO('\x4f\x56\x71\xea')
        m2 = StringIO('abcd')
        m3 = StringIO('\x4f\x56\x71\xea')

        # Create IntegerElements
        intEl1 = IntegerElement(stream=m1, offset=0, size=4, payloadOffset=2)
        intEl1.id = 0x7c
        intEl1.schema = 'mide.xml'
        
        intEl2 = IntegerElement(stream=m2, offset=0, size=4, payloadOffset=2)
        intEl2.id = 0x7c
        intEl2.schema = 'mide.xml'
        
        intEl3 = IntegerElement(stream=m3, offset=0, size=4, payloadOffset=2)
        intEl3.id = 0x7c
        intEl3.schema = 'mide.xml'

        # Assert that the first two elements are not equal
        self.assertNotEqual(intEl1, intEl2)

        # Assert that the first and last elements are equal
        intEl1.stream.seek(0)
        intEl3.stream.seek(0)
        self.assertEqual(intEl1, intEl3)
        
                
    
    def testUIntParse(self):
        """ Test parsing UIntegerElements. """

        self.assertEqual(self.uintEl1.parse(self.mockStream, 2), 64536)
    
    
    
    def testUintEncode(self):
        """ Test encoding UIntegerElements. """

        self.assertEqual(self.uintEl1.encodePayload(0x4142), 'AB')
        


class testFloatElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.FloatElement """
    
    
    
    def setUp(self):
        """ Set up the unit tests with a FloatElement class with some
            custom data (id: 0x4F56, value: 0x3E AA AB).
        """

        self.mockStream = StringIO('\x4f\x56\x3e\xaa\xaa\xab')
                
        self.floatEl = FloatElement(stream=self.mockStream, offset=0, size=4,
                                     payloadOffset=2)
        self.floatEl.id = 0x7c        
        self.floatEl.schema = 'mide.xml'
    
    
    
    def testFloatEq(self):
        """ Test equality of FloatElements with floats. """

        self.assertAlmostEqual(self.floatEl.value, 1.0/3.0)
    
    
    
    def testFloatParse(self):
        """ Test parsing FloatElements. """

        self.mockStream.seek(2)
        self.assertAlmostEqual(self.floatEl.parse(self.mockStream, 4), 1.0/3.0)
    
    
    
    def testFloatEncode(self):
        """ Test encoding FloatElements. """

        self.assertEqual(self.floatEl.encodePayload(1.0/3.0, length=4),
                         '\x3e\xaa\xaa\xab')
        


class testStringElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.StringElement """
    
    
    
    def setUp(self):
        """ Set up the unit tests with a StringElement class with some
            custom data (id: 0x4F40, value: 'bork').
        """

        self.mockStream = StringIO('\x4f\x40bork\x4f\x40bork')
                
        self.strEl1 = StringElement(stream=self.mockStream, offset=0, size=4,
                                     payloadOffset=2)
        self.strEl1.id = 0x7c        
        self.strEl1.schema = 'mide.xml'
                
        self.strEl2 = StringElement(stream=self.mockStream, offset=0, size=4,
                                     payloadOffset=2)
        self.strEl2.id = 0x7c        
        self.strEl2.schema = 'mide.xml'
                
        self.strEl3 = StringElement(stream=self.mockStream, offset=0, size=8,
                                     payloadOffset=2)
        self.strEl3.id = 0x5e        
        self.strEl3.schema = 'matroska.xml'
        
        self.uniEl = UnicodeElement(stream=self.mockStream, offset=0, size=4,
                                    payloadOffset=2)
    
    
    
    def testStringEq(self):
        """ Test equality for StringElements. """

        self.assertEqual(self.strEl1, self.strEl2)
        self.assertNotEqual(self.strEl2, self.strEl3)
    
    
    
    def testStringLen(self):
        """ Test checking the length of StringElements. """

        self.assertEqual(len(self.strEl1), 4)
        self.assertEqual(len(self.strEl3), 8)
    
    
    
    def testStringParse(self):
        """ Test parsing StringElements. """

        self.mockStream.seek(2)
        self.assertEqual(self.strEl1.parse(self.mockStream, 4), 'bork')
    
    
    
    def testStringEncode(self):
        """ Test encoding StringElements. """

        self.assertEqual(self.strEl1.encodePayload('bork'), 'bork')
    
    
    
    def testUnicodeLen(self):
        """ Test getting the length of a UnicodeElement. """

        self.assertEqual(len(self.uniEl), 4)
    
    
    
    def testUnicodeParse(self):
        """ Test parsing UnicodeElements. """

        self.mockStream.seek(2)
        self.assertEqual(self.uniEl.parse(self.mockStream, 4), u'bork')
    
    
    
    def testUnicodeEncode(self):
        """ Test encoding UnicodeElements. """

        self.assertEqual(self.strEl1.encodePayload('bork'), u'bork')
        
        
        
class testDateElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.DataElement """
    
    
    
    def setUp(self):
        """ Set up the unit tests with a DateElement class with some
            custom data (id: 0x80, value: 0x07 71 E1 58 4D 0F 00 00).
        """
                
        self.mockStream = StringIO('\x80\x07\x71\xe1\x58\x4d\x0f\x00\x00')
        
        self.datEl = DateElement(stream=self.mockStream, offset=1, size=8,
                                 payloadOffset=1)
    
    
    
    def testDateParse(self):
        """ Test parsing DateElements. """

        self.mockStream.seek(1)
        self.assertEqual(self.datEl.parse(self.mockStream, 8),
                         datetime.datetime(2018, 1, 1))
    
    
    
    def testDateEncode(self):
        """ Test encoding DateElements. """
        self.assertEqual(self.datEl.encodePayload(datetime.datetime(2018, 1, 1)),
                         '\x07\x71\xe1\x58\x4d\x0f\x00\x00')
    
    

class testBinaryElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.BinaryElement """
    
    
    
    def setUp(self):
        """ Set up the unit tests with a BinaryElement class with some
            custom data.
        """

        self.binEl = BinaryElement(StringIO(), size=2)
    
    
    
    def testBinaryLen(self):
        """ Test getting the length of a BinaryElement. """

        self.assertEqual(len(self.binEl), 2)
    
    
    
class testVoidElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.VoidElement """
    
    
    
    def setUp(self):
        """ Set up the unit tests with a DateElement class with some
            custom data (id: -, value: 0x00 00 00 41).
        """
                
        self.mockStream = StringIO()

        self.mockStream.string = '\x00\x00\x00A'
                
        self.voiEl = VoidElement(stream=self.mockStream, offset=1, size=4,
                                     payloadOffset=1)
        self.voiEl.id = 0x7c        
        self.voiEl.schema = 'mide.xml'
    
    
    
    def testVoidParse(self):
        """ Test parsing a VoidElement. """

        self.assertEqual(self.voiEl.parse(self.mockStream, 4), bytearray())
    
    
    
    def testVoidEncode(self):
        """ Test encoding VoidElements. """

        self.assertEqual(self.voiEl.encodePayload(0x41424344, length=4),
                         '\xff\xff\xff\xff')
    
    
    
class testUnknownElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.UnknownElement """
    
    
    
    def setUp(self):
        """ Set up the unit tests with a DateElement class with some
            custom data (id: -, value: 0x00 00 00 41).
        """
                
        self.mockStream = StringIO()

        self.mockStream.string = '\x00\x00\x00A'
                
        self.unkEl1 = VoidElement(stream=self.mockStream, offset=1, size=4,
                                     payloadOffset=1)
        self.unkEl1.id = 0x7c        
        self.unkEl1.schema = 'mide.xml'
                
        self.unkEl2 = VoidElement(stream=self.mockStream, offset=1, size=4,
                                     payloadOffset=1)
        self.unkEl2.id = 0x7c        
        self.unkEl2.schema = 'mide.xml'
                
        self.unkEl3 = VoidElement(stream=self.mockStream, offset=1, size=4,
                                     payloadOffset=1)
        self.unkEl3.id = 0x7d       
        self.unkEl3.schema = 'mide.xml'
    
    
    
    def testUnknownEq(self):
        """ Test equality between UnknownElements. """

        self.assertEqual(self.unkEl1, self.unkEl2)
        self.assertNotEqual(self.unkEl1, self.unkEl3)
        
        
        
class testMasterElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.MasterElement """
    
    
    
    def setUp(self):
        """ Set up a MasterElement with a single UIntegerElement child. """
        
        schema = loadSchema('./schemata/mide.xml')

        """ Master Element:   ID: 0x1A45DFA3
                            Size: 0x84
                           Value:
                UInt Element:   ID: 0x4286
                              Size: 0x81
                             value: 0x42 
        """
        self.mockStream = StringIO('\x1A\x45\xDF\xA3\x84\x42\x86\x81\x10')
        
        self.element = schema.elements[0x1A45DFA3](stream=self.mockStream,
                                                   offset=0,
                                                   size=4,
                                                   payloadOffset=5)
        self.element.schema = loadSchema('./schemata/mide.xml')
        self.element.id = 0x1A45DFA3
    
    
    
    def testParse(self):
        """ Test parsing MasterElements. """

        masterEl = MasterElement()
        masterEl.id = 0x1A45DFA3
        masterEl.size = 4
        masterEl.schema = loadSchema('./schemata/mide.xml')
        self.assertEqual(masterEl, self.element)
        
        sEbmlVer = self.element.parse()[0]
        sEbmlVer.stream = self.mockStream
        ebmlVer = masterEl.schema.elements[0x4286](masterEl.stream, 5, 1, 8)
        ebmlVer.stream = self.mockStream        
        ebmlVer._value = 16
        self.assertEqual(sEbmlVer, ebmlVer)
    
    
    
    def testParseElement(self):
        """ Test parsing with parseElement. """

        self.mockStream.seek(5)
        newVer = self.element.parseElement(self.mockStream)[0]
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        
        self.assertEqual(newVer, ebmlVer)
    
    
    
    def testIter(self):
        """ Test getting an iterator from a MasterElement. """

        self.mockStream.seek(5)
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        
        self.assertEqual(list(self.element), [ebmlVer])
    
    
    
    def testLen(self):
        """ Test getting the length of a MasterElement. """

        self.assertEqual(len(self.element), 0)
    
    
    
    def testValue(self):
        """ Test getting the value of MasterElements. """

        self.mockStream.seek(5)
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        self.assertEqual(self.element.value, [ebmlVer])
    
    
    
    def testGetItem(self):
        """ Test getting items from MasterElements. """

        self.mockStream.seek(5)
        
        ebmlVer = self.element.schema.elements[0x4286](self.mockStream, 5, 1, 8)
        self.assertEqual(self.element[0], ebmlVer)
    
    
    
    def testGc(self):
        """ Test getting the cache from MasterElements. """

        self.assertIsNone(self.element._value)

        self.element.value
        self.assertIsNotNone(self.element._value)

        self.element.gc()
        self.assertIsNone(self.element._value)
    
    
    
    def testEncodePayload(self):
        """ Test encoding the payload of a MasterElement. """

        self.assertEqual(self.element.encodePayload({0x4286:16}),
                         bytearray('\x42\x86\x81\x10'))
    
    
    
    def testEncode(self):
        """ Test encoding MasterElements. """

        self.assertEqual(self.element.encode({0x4286:16}),
                         bytearray('\x1A\x45\xDF\xA3\x84\x42\x86\x81\x10'))
    
    
    
    def testDump(self):
        """ Test dumping the contents of a MasterElement. """

        self.assertEqual(self.element.dump(),
                         collections.OrderedDict([['EBMLVersion', 16]]))
        
        
        
class testDocument(unittest.TestCase):
    """ Unit tests for ebmlite.core.Document """
    
    
    
    def setUp(self):
        """ Set up a Schema from mide.xml and create a Document from an IDE file. """

        self.schema = loadSchema('./schemata/mide.xml')
        self.doc = self.schema.load('./tests/SSX46714-doesnot.IDE')
        
        self.stream = StringIO('test')
    
    
    
    def testClose(self):
        """ Test closing the stream in a Document """

        self.assertFalse(self.doc.stream.closed)
        self.doc.close()
        self.assertTrue(self.doc.stream.closed)
    
    
    
    def testValue(self):
        """ Test getting the value from a Document. """

        self.assertEqual([x for x in self.doc], [x for x in self.doc.value])
        self.assertEqual(type(self.doc.value), types.GeneratorType)
    
    
    
    def testVersion(self):
        """ Test getting the version of a Document. """

        self.assertEqual(self.doc.version, 2)
        self.doc.info['DocTypeVersion'] = 5
        self.assertEqual(self.doc.version, 5)
    
    
    
    def testType(self):
        """ Test getting the type of a Document. """

        self.assertEqual(self.doc.type, 'mide')
        self.doc.info['DocType'] = 'bork'
        self.assertEqual(self.doc.type, 'bork')
    
    
    
    def testEncode(self):
        """ Test encoding a Document. """

        self.stream = StringIO()
        self.doc.encode(self.stream, {0x52A1:50})
        self.stream.seek(0)
        self.assertEqual(self.stream.buf, '\x52\xA1\x81\x32')



class testSchema(unittest.TestCase):
    """ Unit tests for ebmlite.core.Schema """
    
    
    
    def setUp(self):
        """ Set up a new Schema.  It is necessary to clear the cache to
            properly run tests.
        """

        import core
        core.SCHEMATA = {}
        self.schema = loadSchema('./schemata/mide.xml')
        
        self.stream = StringIO('test')
    
    
    
    def testAddElement(self):
        """ Test adding elements to a schema. """

        self.assertNotIn(0x4DAB, self.schema.elements.keys())
        self.schema.addElement(0x4dab, 'Dabs', StringElement)
        self.assertIn(0x4DAB, self.schema.elements.keys())
        cls = self.schema[0x4DAB]
        self.assertEqual(cls.id, 0x4DAB)
        self.assertEqual(cls.name, 'Dabs')
        self.assertEqual(cls.schema, self.schema)
    
    
    
    def testGet(self):
        """ Test getting elements from a Schema. """

        self.assertEqual(self.schema.get(0x1A45DFA3).name, 'EBML')
        self.assertIsNone(self.schema.get(-1))
        self.assertEqual(self.schema.get(-1, 5), 5)
    
    
    
    def testLoad(self):
        """ Test loading EMBL files with a Schema. """

        ide = self.schema.load('./tests/SSX46714-doesnot.IDE')
        self.assertEqual(dict(ide.info), 
                         {'DocTypeVersion':2, 'EBMLVersion':1,
                          'EBMLMaxIDLength':4, 'EBMLReadVersion':1,
                          'EBMLMaxSizeLength':8, 'DocTypeReadVersion':2, 
                          'DocType':'mide'})
    
    
    
    def testLoads(self):
        """ Test laoding EBML strings with a Schema. """

        with open('./tests/SSX46714-doesnot.IDE', 'rb') as f:
            s = f.read()
        ide = self.schema.loads(s)
        self.assertEqual(dict(ide.info), 
                         {'DocTypeVersion':2, 'EBMLVersion':1,
                          'EBMLMaxIDLength':4, 'EBMLReadVersion':1,
                          'EBMLMaxSizeLength':8, 'DocTypeReadVersion':2, 
                          'DocType':'mide'})
    
    
    
    def testVersion(self):
        """ Test getting the version of a Schema. """

        self.assertEqual(self.schema.version, 2)
    
    
    
    def testType(self):
        """ Test getting the type of a Schema. """

        self.assertEqual(self.schema.type, 'mide')
    
    
    
    def testEncode(self):
        """ Test encoding an Element with a Schema. """

        stream = StringIO('')
        self.schema.encode(stream, {0x52A1:50})
        stream.seek(0)
        self.assertEqual(stream.buf, '\x52\xA1\x81\x32')
    
    
    
    def testEncodes(self):
        """ Test encoding an Element with a Schema from a string. """

        self.assertEqual(self.schema.encodes({0x52A1:50}), '\x52\xA1\x81\x32')
    
    
    
    def testVerify(self):
        """ Test verifying a string as valid with a Schema. """

        self.assertTrue(self.schema.verify('\x42\x86\x81\x01'))
        with self.assertRaises(IOError):
            self.schema.verify('\x00\x42\x86\x81\x01')
        
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()