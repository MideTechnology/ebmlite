import collections
import datetime
import os.path
import sys
import types
import unittest
from io import BytesIO

from ebmlite.core import listSchemata, loadSchema, parseSchema, \
    BinaryElement, DateElement, Element, FloatElement, IntegerElement, \
    MasterElement, StringElement, UIntegerElement, UnicodeElement, \
    VoidElement, UnknownElement, SCHEMATA, SCHEMA_PATH


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
        self.mockStream = BytesIO(b'\x4f\x56\x71\xea')

        GenericElement = type('GenericElement', (Element,),
                              {'id': 0x4343, 'name': 'Generic Element',
                               'schema':loadSchema('./ebmlite/schemata/mide_ide.xml'),
                               'mandatory': False, 'multiple': False,
                               'precache': False, 'length': 4, 'children': dict(),
                               '__doc__': 'no'})

        self.element = GenericElement(stream=self.mockStream, offset=0, size=4,
                               payloadOffset=2)



    def testParse(self):
        """ Test parsing a generic element as a bytestring. """

        self.assertEqual(self.element.parse(self.mockStream, 4), b'\x4f\x56\x71\xea')



    def testValue(self):
        """ Test getting a value from a generic element as a bytestring. """

        # Test first parse
        self.assertEqual(self.element.value, b'\x71\xea')

        # Test that mockstring is empty and that the value has been cached
        self.assertEqual(self.mockStream.tell(), 4)
        self.assertEqual(self.element.value, b'\x71\xea')



    def testGetRaw(self):
        """ Test getting a raw bytestring of a full generic element. """

        self.assertEqual(self.element.getRaw(), b'\x4f\x56\x71\xea')



    def testGetRawValue(self):
        """ Test getting a raw bytestring of the data from a generic element. """

        self.assertEqual(self.element.getRawValue(), b'\x71\xea')



    def testGc(self):
        """ Test clearing caches. """

        self.assertEqual(self.element._value, None)
        self.assertEqual(self.element.gc(), 0)

        _ = self.element.value  # `value` is a property that affects `_value`
        self.assertEqual(self.element._value, b'\x71\xea')

        self.assertEqual(self.element.gc(), 1)
        self.assertEqual(self.element._value, None)



    def testEncodePayload(self):
        """ Test encoding a payload. """

        self.assertEqual(self.element.encodePayload(b'\x4f\x56\x71\xea', length=4),
                         b'\x4f\x56\x71\xea')



    def testEncode(self):
        """ Test encoding a full EBML element. """

        self.assertEqual(self.element.encode(b'\x71\xea', 2), b'CC\x82\x71\xea')
        pass



    def testDump(self):
        """Test dumping an element to a dict"""

        self.assertEqual(self.element.dump(), b'\x71\xea')



class testIntElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.IntElement """



    def setUp(self):
        """ Set up the unit tests with an IntegerElement class with some
            custom data (id: -, value: 0xFC18).
        """

        # -1000 = -0b0000 0011  1110 1000 =>
        # 0b1111 1100  0001 1000 =>
        # 0xfc18
        self.mockStream = BytesIO(b'\xfc\x18')

        mide_schema = loadSchema('mide_ide.xml')
        eclass1 = type('IntEl1Element', (IntegerElement,),
                      {'id':0x7c, 'name': 'IntEl1', 'schema':mide_schema,
                       '__slots__': IntegerElement.__slots__})

        eclass2 = type('UIntEl1Element', (UIntegerElement,),
                      {'id':0x7c, 'name': 'UIntEl1', 'schema':mide_schema,
                       '__slots__': UIntegerElement.__slots__})

        self.intEl1 = eclass1(stream=self.mockStream, offset=0, size=4,
                              payloadOffset=2)
        self.uintEl1 = eclass2(stream=self.mockStream, offset=0, size=4,
                               payloadOffset=2)



    def testIntParse(self):
        """ Test parsing an IntegerElement. """

        self.assertEqual(self.intEl1.parse(self.mockStream, 2), -1000)



    def testIntEncode(self):
        """ Test encoding an IntegerElement. """

        self.assertEqual(self.intEl1.encodePayload(0x4242, 2), b'BB')
        self.assertEqual(self.intEl1.encodePayload(-1000, 2), b'\xfc\x18')



    def testIntEq(self):
        """ Test equality of IntegerElements. """

        # Define buffers for IntegerElements
        m1 = BytesIO(b'\x4f\x56\x71\xea')
        m2 = BytesIO(b'abcd')
        m3 = BytesIO(b'\x4f\x56\x71\xea')

        # Create IntegerElements
        mide_schema = loadSchema('mide_ide.xml')
        eclass1 = type('IntEl1Element', (IntegerElement,),
                      {'id':0x7c, 'name': 'IntEl1', 'schema':mide_schema,
                       '__slots__': IntegerElement.__slots__})
        eclass2 = type('IntEl2Element', (IntegerElement,),
                      {'id':0x7c, 'name': 'IntEl2', 'schema':mide_schema,
                       '__slots__': IntegerElement.__slots__})
        eclass3 = type('IntEl3Element', (IntegerElement,),
                      {'id':0x7c, 'name': 'IntEl3', 'schema':mide_schema,
                       '__slots__': IntegerElement.__slots__})

        intEl1 = eclass1(stream=m1, offset=0, size=4, payloadOffset=2)
        intEl2 = eclass2(stream=m2, offset=0, size=4, payloadOffset=2)
        intEl3 = eclass3(stream=m3, offset=0, size=4, payloadOffset=2)

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

        self.assertEqual(self.uintEl1.encodePayload(0x4142), b'AB')



class testFloatElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.FloatElement """



    def setUp(self):
        """ Set up the unit tests with a FloatElement class with some
            custom data (id: 0x4F56, value: 0x3E AA AB).
        """

        self.mockStream = BytesIO(b'\x4f\x56\x3e\xaa\xaa\xab')

        mide_schema = loadSchema('mide_ide.xml')
        eclass1 = type('FloatEl1Element', (FloatElement,),
                      {'id':0x7c, 'name': 'FloatEl1', 'schema':mide_schema,
                       '__slots__': FloatElement.__slots__})

        self.floatEl = eclass1(stream=self.mockStream, offset=0, size=4,
                               payloadOffset=2)



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
                         b'\x3e\xaa\xaa\xab')



class testStringElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.StringElement """



    def setUp(self):
        """ Set up the unit tests with a StringElement class with some
            custom data (id: 0x4F40, value: 'bork').
        """

        self.mockStream = BytesIO(b'\x4f\x40bork\x4f\x40bork')

        mide_schema = loadSchema('mide_ide.xml')
        matroska_schema = loadSchema('matroska.xml')

        eclass1 = type('StrEl1Element', (StringElement,),
                      {'id':0x7c, 'name': 'StrEl1', 'schema': mide_schema,
                       '__slots__': StringElement.__slots__})

        eclass2 = type('StrEl2Element', (StringElement,),
                      {'id':0x7c, 'name': 'StrEl2', 'schema': mide_schema,
                       '__slots__': StringElement.__slots__})

        eclass3 = type('StrEl3Element', (StringElement,),
                      {'id':0x5e, 'name': 'StrEl3', 'schema': matroska_schema,
                       '__slots__': StringElement.__slots__})

        self.strEl1 = eclass1(stream=self.mockStream, offset=0, size=4,
                            payloadOffset=2)

        self.strEl2 = eclass2(stream=self.mockStream, offset=0, size=4,
                                     payloadOffset=2)

        self.strEl3 = eclass3(stream=self.mockStream, offset=0, size=8,
                                     payloadOffset=2)


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

        self.assertEqual(self.strEl1.encodePayload(b'bork'), b'bork')



    def testUnicodeLen(self):
        """ Test getting the length of a UnicodeElement. """

        self.assertEqual(len(self.uniEl), 4)



    def testUnicodeParse(self):
        """ Test parsing UnicodeElements. """

        self.mockStream.seek(2)
        self.assertEqual(self.uniEl.parse(self.mockStream, 4), u'bork')



    def testUnicodeEncode(self):
        """ Test encoding UnicodeElements. """

        self.assertEqual(self.strEl1.encodePayload(u'bork'), b'bork')
        self.assertEqual(self.strEl1.encodePayload(u'börk'), b'b?rk')



class testDateElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.DataElement """



    def setUp(self):
        """ Set up the unit tests with a DateElement class with some
            custom data (id: 0x80, value: 0x07 71 E1 58 4D 0F 00 00).
        """

        self.mockStream = BytesIO(b'\x80\x07\x71\xe1\x58\x4d\x0f\x00\x00')

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
                         b'\x07\x71\xe1\x58\x4d\x0f\x00\x00')



class testBinaryElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.BinaryElement """



    def setUp(self):
        """ Set up the unit tests with a BinaryElement class with some
            custom data.
        """

        self.binEl = BinaryElement(BytesIO(), size=2)



    def testBinaryLen(self):
        """ Test getting the length of a BinaryElement. """

        self.assertEqual(len(self.binEl), 2)



class testVoidElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.VoidElement """



    def setUp(self):
        """ Set up the unit tests with a DateElement class with some
            custom data (id: -, value: 0x00 00 00 41).
        """

        self.mockStream = BytesIO()

        self.mockStream.string = b'\x00\x00\x00A'

        mide_schema = loadSchema('mide_ide.xml')
        eclass1 = type('VoidEl1Element', (VoidElement,),
                      {'schema':mide_schema, 'id':0xEC,
                       '__slots__': VoidElement.__slots__})

        self.voiEl = eclass1(stream=self.mockStream, offset=1, size=4,
                             payloadOffset=1)



    def testVoidParse(self):
        """ Test parsing a VoidElement. """

        self.assertEqual(self.voiEl.parse(self.mockStream, 4), bytearray())



    def testVoidEncode(self):
        """ Test encoding VoidElements. """

        self.assertEqual(self.voiEl.encodePayload(0x41424344, length=4),
                         b'\xff\xff\xff\xff')



class testUnknownElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.UnknownElement """



    def setUp(self):
        """ Set up the unit tests with a DateElement class with some
            custom data (id: -, value: 0x00 00 00 41).
        """

        self.mockStream = BytesIO()
        self.mockStream.string = b'\x00\x00\x00A'

        mide_schema = loadSchema('mide_ide.xml')
        self.unkEl1 = UnknownElement(stream=self.mockStream, offset=1, size=4,
                                  payloadOffset=1, schema=mide_schema, eid=0x7c)

        self.unkEl2 = UnknownElement(stream=self.mockStream, offset=1, size=4,
                                  payloadOffset=1, schema=mide_schema, eid=0x7c)

        self.unkEl3 = UnknownElement(stream=self.mockStream, offset=1, size=4,
                                  payloadOffset=1, schema=mide_schema, eid=0x7d)



    def testUnknownEq(self):
        """ Test equality between UnknownElements. """

        self.assertEqual(self.unkEl1, self.unkEl2)
        self.assertNotEqual(self.unkEl1, self.unkEl3)



class testMasterElements(unittest.TestCase):
    """ Unit tests for ebmlite.core.MasterElement """



    def setUp(self):
        """ Set up a MasterElement with a single UIntegerElement child. """

        schema = loadSchema('./ebmlite/schemata/mide_ide.xml')

        """ Master Element:   ID: 0x1A45DFA3
                            Size: 0x84
                           Value:
                UInt Element:   ID: 0x4286
                              Size: 0x81
                             value: 0x42
        """
        self.mockStream = BytesIO(b'\x1A\x45\xDF\xA3\x84\x42\x86\x81\x10')

        self.element = schema.elements[0x1A45DFA3](stream=self.mockStream,
                                                   offset=0,
                                                   size=4,
                                                   payloadOffset=5)



    def testParse(self):
        """ Test parsing MasterElements. """

        eclass1 = type('MasterEl1Element', (MasterElement,),
                      {'id':0x1A45DFA3, 'name': 'MasterEl1',
                       'schema':self.element.schema,
                       '__slots__': MasterElement.__slots__})

        masterEl = eclass1(self.mockStream, offset=0, size=4, payloadOffset=5)
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

        self.assertEqual(len(self.element), 1)



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
                         bytearray(b'\x42\x86\x81\x10'))



    def testEncode(self):
        """ Test encoding MasterElements. """

        self.assertEqual(self.element.encode({0x4286:16}),
                         bytearray(b'\x1A\x45\xDF\xA3\x84\x42\x86\x81\x10'))



    def testDump(self):
        """ Test dumping the contents of a MasterElement. """

        self.assertEqual(self.element.dump(),
                         collections.OrderedDict([['EBMLVersion', 16]]))



class testDocument(unittest.TestCase):
    """ Unit tests for ebmlite.core.Document """



    def setUp(self):
        """ Set up a Schema from mide_ide.xml and create a Document from an IDE file. """

        self.schema = loadSchema('./ebmlite/schemata/mide_ide.xml')
        self.doc = self.schema.load('./tests/SSX46714-doesnot.IDE')

        self.stream = BytesIO(b'test')



    def testEnterExit(self):
        """Test using the document in a context manager."""

        class CustomException(Exception):
            pass

        self.assertFalse(self.doc.stream.closed)
        try:
            with self.doc:
                raise CustomException()
        except CustomException:
            pass
        self.assertTrue(self.doc.stream.closed)



    def testClose(self):
        """ Test closing the stream in a Document """

        self.assertFalse(self.doc.stream.closed)
        self.doc.close()
        self.assertTrue(self.doc.stream.closed)
        self.doc.close()

        with open('./tests/SSX46714-doesnot.IDE', 'rb') as file:
            doc = self.schema.load(file)
            self.assertFalse(file.closed)
            doc.close()
            self.assertFalse(file.closed)


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

        self.stream = BytesIO()
        self.doc.encode(self.stream, {0x52A1:50})
        self.stream.seek(0)
        self.assertEqual(self.stream.getvalue(), b'\x52\xA1\x81\x32')



class testSchema(unittest.TestCase):
    """ Unit tests for ebmlite.core.Schema """



    def setUp(self):
        """ Set up a new Schema.  It is necessary to clear the cache to
            properly run tests.
        """

        from ebmlite import core
        core.SCHEMATA = {}
        self.schema = loadSchema('./ebmlite/schemata/mide_ide.xml')

        self.stream = BytesIO(b'test')


    def testAddElement(self):
        """ Test adding elements to a schema. """

        self.assertNotIn(0x4DAB, list(self.schema.elements.keys()))
        self.schema.addElement(0x4dab, 'Dabs', StringElement)
        self.assertIn(0x4DAB, list(self.schema.elements.keys()))
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
        self.assertEqual({'DocTypeVersion': 2,    'EBMLVersion': 1,
                          'EBMLMaxIDLength': 4,   'EBMLReadVersion': 1,
                          'EBMLMaxSizeLength': 8, 'DocTypeReadVersion': 2,
                          'DocType': 'mide'},
                         dict(ide.info))



    def testLoads(self):
        """ Test laoding EBML strings with a Schema. """

        with open('./tests/SSX46714-doesnot.IDE', 'rb') as f:
            s = f.read()
        ide = self.schema.loads(s)
        self.assertEqual(dict(ide.info),
                         {'DocTypeVersion':2, 'EBMLVersion':1,
                          'EBMLMaxIDLength':4, 'EBMLReadVersion':1,
                          'EBMLMaxSizeLength':8, 'DocTypeReadVersion':2,
                          'DocType': 'mide'})



    def testVersion(self):
        """ Test getting the version of a Schema. """

        self.assertEqual(self.schema.version, 2)



    def testType(self):
        """ Test getting the type of a Schema. """

        self.assertEqual(self.schema.type, 'mide')



    def testEncode(self):
        """ Test encoding an Element with a Schema. """

        stream = BytesIO(b'')
        self.schema.encode(stream, {0x52A1:50})
        stream.seek(0)
        self.assertEqual(stream.getvalue(), b'\x52\xA1\x81\x32')



    def testEncodes(self):
        """ Test encoding an Element with a Schema from a string. """

        self.assertEqual(self.schema.encodes({0x52A1:50}), b'\x52\xA1\x81\x32')



    def testVerify(self):
        """ Test verifying a string as valid with a Schema. """

        self.assertTrue(self.schema.verify(b'\x42\x86\x81\x01'))
        with self.assertRaises(IOError):
            self.schema.verify(b'\x00\x42\x86\x81\x01')


    def testLoadSchema(self):
        """ Test schema loading. If things have gotten this far, basic
            loading works; this tests some additional features.
       """

        # Back up schemata so this test starts fresh
        schemata = SCHEMATA.copy()
        SCHEMATA.clear()

        schema1 = loadSchema('mide_ide.xml')
        schema2 = loadSchema('./ebmlite/schemata/mide_ide.xml')

        self.assertTrue(schema1 is schema2,
                        "loadSchema() did not use cached parsed schema")

        schema3 = loadSchema('mide_ide.xml', reload=True)

        self.assertTrue(schema1 is not schema3,
                        "loadSchema() did not reload schema")

        # Restore schemata
        SCHEMATA.clear()
        SCHEMATA.update(schemata)


    def testParseSchema(self):
        """ Test parsing a schema from a string. """

        filename = self.schema.filename
        ids = list(sorted(self.schema.elements))

        with open(filename, 'r') as f:
            xml = f.read()

        schema = parseSchema(xml, name=filename)
        self.assertTrue(schema is self.schema,
                        "parseSchema() did not use cached loaded schema")

        schema = parseSchema(xml, name="testParseSchema")
        self.assertTrue(schema is not self.schema,
                        "parseSchema() did not produce a new schema")
        self.assertEqual(schema, self.schema,
                         "Parsed schema string did not match loaded schema")

        # Just in case `Schema.__eq__()` has an error:
        self.assertEqual(list(sorted(schema.elements)), ids,
                         "Parsed schema string did not match loaded schema")

        schema2 = parseSchema(xml, name="testParseSchema")
        self.assertTrue(schema2 is schema,
                        "parseSchema() did not use cached parsed schema")


    def testSchemaModulePath(self):
        """ Test schema loading using module-relative paths. """
        sys.path.insert(0, os.path.dirname(__file__))

        SCHEMATA.clear()
        schema1 = loadSchema("{module_path_testing}/test_schema.xml")

        SCHEMA_PATH.insert(0, '{module_path_testing}')
        schema2 = loadSchema("test_schema2.xml")

        SCHEMA_PATH.pop(0)


    def testListSchemata(self):
        """ Test schema gathering. """
        sys.path.insert(0, os.path.dirname(__file__))
        SCHEMA_PATH.insert(0, '{module_path_testing}')

        schemata = listSchemata()

        for name, paths in schemata.items():
            byName = loadSchema(name)
            byPath = [loadSchema(p) for p in paths]

            self.assertEqual(byName, byPath[0],
                             "Base schema name did not load expected default")

        # NOTE: This will need to be changed if/when enDAQ schemata removed
        #  from package.
        self.assertIn('mide_manifest.xml', schemata,
                      'mide_manifest.xml not found in {}'.format(schemata))
        self.assertGreaterEqual(len(schemata['mide_manifest.xml']), 2,
                         "listSchemata() did not find all mide_manifest.xml schemata")

        SCHEMA_PATH.pop(0)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
