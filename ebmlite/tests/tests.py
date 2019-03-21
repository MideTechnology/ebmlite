'''
Created on Aug 14, 2017

@author: dstokes
'''
import sys
import unittest
from xml.dom.minidom import parseString
from xml.etree import ElementTree as ET

import numpy as np

import core
import util


class Test(unittest.TestCase):
    """ Integration tests for util.py """



    def testMkv(self):
        """ Test the functionality of the ebmlite library by converting a known
            good MKV file (a derivative of EBML) back and forth, then compare
            the results.
        """
        schemaFile = './schemata/matroska.xml'
        ebmlFile1 = './tests/video-1.mkv'
        ebmlFile2 = './tests/video-2.mkv'
        xmlFile1 = './tests/video-1.xml'
        xmlFile2 = './tests/video-2.xml'

        schema = core.loadSchema(schemaFile)

        # Start with toXml
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot = util.toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot, encoding='latin-1')

        # Save xml
        with open(xmlFile1, 'wb') as f:
            xmlString1 = xmlString1.decode('latin-1').replace('><', '>\r\n<')
            if sys.version_info.major == 3:
                f.write(xmlString1.encode('latin-1'))
            else:
                f.write(bytearray(xmlString1, 'latin-1'))

        # Convert xml2ebml
        with open(ebmlFile2, 'wb') as out:
            util.xml2ebml(xmlFile1, out, schema)

        # write the second xml file
        ebmlDoc2 = schema.load(ebmlFile2, headers=True)
        mkvRoot2 = util.toXml(ebmlDoc2)
        xmlString2 = ET.tostring(mkvRoot2, encoding='latin-1')
        # self.assertEqual(xmlString1, xmlString2, "xml strings aren't matching up")
        with open(xmlFile2, 'wt') as f:
            xmlString2 = xmlString2.decode('latin-1').replace('><', '>\r\n<')
            if sys.version_info.major == 3:
                f.write(xmlString2)
            else:
                f.write(bytearray(xmlString2, 'latin-1'))

        # Load back the XML files in order to compare the two
        xmlDoc1 = util.loadXml(xmlFile1, schema)
        xmlDoc2 = util.loadXml(xmlFile2, schema)

        # Compare each element from the XML
        xmlEls1 = [xmlDoc1]
        xmlEls2 = [xmlDoc2]
        while len(xmlEls1) > 0:
            self.assertEqual(xmlEls1[0], xmlEls2[0], 'Element '
                             + repr(xmlEls1[0])
                             + ' was not converted properly')
            for x in xmlEls1.pop(0).children.values():
                if issubclass(x, core.Element):
                    xmlEls1.append(x)
            for x in xmlEls2.pop(0).children.values():
                if issubclass(x, core.Element):
                    xmlEls2.append(x)

        np.testing.assert_array_equal(xmlString1, xmlString2)


    def testIde(self):
        """ Test the functionality of the ebmlite library by converting a known
            good IDE file (a derivative of EBML) back and forth, then compare
            the results.
        """
        schemaFile = u'./schemata/mide_ide.xml'
        ebmlFile1 = u'./tests/SSX46714-doesnot.IDE'
        ebmlFile2 = u'./tests/SSX46714-new.IDE'
        xmlFile1 = u'./tests/ssx-1.xml'
        xmlFile2 = u'./tests/ssx-2.xml'

        schema = core.loadSchema(schemaFile)

        # Start with toXml
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot = util.toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot, encoding='utf-8')

        # Save xml
        with open(xmlFile1, 'wb') as f:
            f.write(xmlString1.replace(b'><', b'>\r\n<'))

        # Convert xml2ebml
        with open(ebmlFile2, 'wb') as out:
            util.xml2ebml(xmlFile1, out, schema, sizeLength=4)

        # write the second xml file
        ebmlDoc2 = schema.load(ebmlFile2, headers=True)
        mkvRoot2 = util.toXml(ebmlDoc2)
        xmlString2 = ET.tostring(mkvRoot2, encoding='latin-1')
        with open(xmlFile2, 'wb') as f:
            f.write(xmlString2.replace(b'><', b'>\r\n<'))

        # Load back the XML files in order to compare the two
        xmlDoc1 = util.loadXml(xmlFile1, schema)
        xmlDoc2 = util.loadXml(xmlFile2, schema)

        # Compare each element from the XML
        xmlEls1 = [xmlDoc1]
        xmlEls2 = [xmlDoc2]
        while len(xmlEls1) > 0:
            self.assertEqual(xmlEls1[0], xmlEls2[0], 'Element '
                             + repr(xmlEls1[0])
                             + ' was not converted properly')
            for x in xmlEls1.pop(0).children.values():
                if issubclass(x, core.Element):
                    xmlEls1.append(x)
            for x in xmlEls2.pop(0).children.values():
                if issubclass(x, core.Element):
                    xmlEls2.append(x)

        np.testing.assert_array_equal(xmlString1, xmlString2)



    def testPPrint(self):
        """ Test pretty-printing EBML files. """
        schemaFile = './schemata/mide_ide.xml'
        schema = core.loadSchema(schemaFile)

        ebmlDoc = schema.load('./tests/SSX46714-doesnot.IDE', headers=True)

        with open('./tests/IDE-Pretty.txt', 'wb') as f:
            util.pprint(ebmlDoc, out=f)

        xmlString = ET.tostring(util.toXml(ebmlDoc))
        with open('./tests/IDE-Pretty.xml', 'wb') as prettyXmlFile:
            parseString(xmlString).writexml(prettyXmlFile,
                                            addindent='\t',
                                            newl='\n',
                                            encoding='latin-1')


    def testInfiniteElement(self):
        """ Test parsing an EBML file with an infinite-length element. """
        schemaFile = './schemata/matroska.xml'
        ebmlFile1 = './tests/video-2.mkv'
        ebmlFile2 = './tests/video-3.mkv'

        schema = core.loadSchema(schemaFile)

        # Convert the MKV files into human-readable xml strings
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot1 = util.toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot1, encoding='latin-1')
        xmlString1 = xmlString1.replace('><'.encode('latin-1'), '>\r\n<'.encode('latin-1'))

        ebmlDoc2 = schema.load(ebmlFile2, headers=True)
        ebmlRoot2 = util.toXml(ebmlDoc2)
        xmlString2 = ET.tostring(ebmlRoot2, encoding='latin-1')
        xmlString2 = xmlString2.replace('><'.encode('latin-1'), '>\r\n<'.encode('latin-1'))

        # Convert the xml strings into lists of lines to make comparison easier,
        # dropping the second line because that will reference different source
        # file names
        xmlLines1 = xmlString1.splitlines()
        xmlLines1 = xmlLines1[2:]
        xmlLines2 = xmlString2.splitlines()
        xmlLines2 = xmlLines2[2:]

        # Compare as lists to narrow the location of any differences
        #self.assertListEqual(xmlLines1, xmlLines2,
        #                     'One or more lines are different in the xml documents')

        np.testing.assert_array_equal(xmlString1, xmlString2)


if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
