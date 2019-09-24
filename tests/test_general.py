'''
Created on Aug 14, 2017

@author: dstokes
'''
import unittest
from xml.dom.minidom import parseString
from xml.etree import ElementTree as ET

from ebmlite import core
from ebmlite import util


class Test(unittest.TestCase):
    """ Integration tests for util.py """



    def testMkv(self):
        """ Test the functionality of the ebmlite library by converting a known
            good MKV file (a derivative of EBML) back and forth, then compare
            the results.
        """
        schemaFile = './ebmlite/schemata/matroska.xml'
        ebmlFile1 = './tests/video-1.mkv'
        ebmlFile2 = './tests/video-1-copy.mkv'
        xmlFile1 = './tests/video-1.xml'
        xmlFile2 = './tests/video-1-copy.xml'

        schema = core.loadSchema(schemaFile)

        # Start with toXml
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot = util.toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot, encoding='UTF-8')

        # Save xml
        with open(xmlFile1, 'wt') as f:
            f.write(xmlString1)

        # Convert xml2ebml
        with open(ebmlFile2, 'wb') as out:
            util.xml2ebml(xmlFile1, out, schema)

        # write the second xml file
        ebmlDoc2 = schema.load(ebmlFile2, headers=True)
        mkvRoot2 = util.toXml(ebmlDoc2)
        xmlString2 = ET.tostring(mkvRoot2, encoding='UTF-8')
        # self.assertEqual(xmlString1, xmlString2, "xml strings aren't matching up")
        with open(xmlFile2, 'wt') as f:
            f.write(xmlString2)

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


    def testIde(self):
        """ Test the functionality of the ebmlite library by converting a known
            good IDE file (a derivative of EBML) back and forth, then compare
            the results.
        """
        schemaFile = './ebmlite/schemata/mide_ide.xml'
        ebmlFile1 = './tests/SSX46714-doesnot.IDE'
        ebmlFile2 = './tests/SSX46714-new.IDE'
        xmlFile1 = './tests/ssx-1.xml'
        xmlFile2 = './tests/ssx-2.xml'

        schema = core.loadSchema(schemaFile)

        # Start with toXml
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot = util.toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot, encoding='UTF-8')

        # Save xml
        with open(xmlFile1, 'wt') as f:
            f.write(xmlString1.replace('><', '>\r\n<'))

        # Convert xml2ebml
        with open(ebmlFile2, 'wb') as out:
            util.xml2ebml(xmlFile1, out, schema)

        # write the second xml file
        ebmlDoc2 = schema.load(ebmlFile2, headers=True)
        mkvRoot2 = util.toXml(ebmlDoc2)
        xmlString2 = ET.tostring(mkvRoot2, encoding='UTF-8')
        with open(xmlFile2, 'wt') as f:
            f.write(xmlString2.replace('><', '>\r\n<'))

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



    def testPPrint(self):
        """ Test pretty-printing EBML files. """
        schemaFile = './ebmlite/schemata/mide_ide.xml'
        schema = core.loadSchema(schemaFile)

        ebmlDoc = schema.load('./tests/SSX46714-doesnot.IDE', headers=True)

        util.pprint(ebmlDoc, out=open('./tests/IDE-Pretty.txt', 'wt'))
        xmlString = ET.tostring(util.toXml(ebmlDoc))
        prettyXmlFile = open('./tests/IDE-Pretty.xml', 'wt')
        parseString(xmlString).writexml(prettyXmlFile,
                                        addindent='\t',
                                        newl='\n',
                                        encoding='utf-8')


    def testInfiniteElement(self):
        """ Test parsing an EBML file with an infinite-length element. """
        schemaFile = './ebmlite/schemata/matroska.xml'
        ebmlFile1 = './tests/video-2.mkv'
        ebmlFile2 = './tests/video-3.mkv'

        schema = core.loadSchema(schemaFile)

        # Convert the MKV files into human-readable xml strings
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot1 = util.toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot1, encoding='UTF-8').replace('><', '>\r\n<')

        ebmlDoc2 = schema.load(ebmlFile2, headers=True)
        ebmlRoot2 = util.toXml(ebmlDoc2)
        xmlString2 = ET.tostring(ebmlRoot2, encoding='UTF-8').replace('><', '>\r\n<')

        # Convert the xml strings into lists of lines to make comparison easier,
        # dropping the second line because that will reference different source
        # file names
        xmlLines1 = xmlString1.splitlines()
        xmlLines1 = [xmlLines1[0]] + xmlLines1[2:]
        xmlLines2 = xmlString2.splitlines()
        xmlLines2 = [xmlLines2[0]] + xmlLines2[2:]

        # Compare as lists to narrow the location of any differences
        self.assertListEqual(xmlLines1, xmlLines2,
                             'One or more lines are different in the xml documents')


if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
