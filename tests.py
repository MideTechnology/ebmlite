'''
Created on Aug 14, 2017

@author: dstokes
'''
import unittest
import core
import os, sys
import numpy as np
from datetime import datetime, timedelta
from difflib import ndiff
from xml.dom.minidom import parseString

from core     import *
from decoding import *
from encoding import *
from mock     import *
from numpy    import inf
from util     import *


    
class MockStream(object):
    def __init__(self, string=None):
        self.string = '' if string is None else string
        self.position = 0
        self.isClosed = False
    
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
    
    def close(self):
        self.isClosed = True
        
    def write(self, str):
        self.string += str
        
        

class Test(unittest.TestCase):


    def setUp(self):
        pass

    
    
    def tearDown(self):
        pass
    
    
    
    def testMkv(self):
        schemaFile = '.\\schemata\\matroska.xml'
        ebmlFile1 = '.\\testFiles\\video-1.mkv'
        ebmlFile2 = '.\\testFiles\\video-2.mkv'
        xmlFile1 = '.\\testFiles\\video-1.xml'
        xmlFile2 = '.\\testFiles\\video-2.xml'
        
        schema = core.loadSchema(schemaFile)
        
        # Start with toXml
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot = toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot, encoding='UTF-8')
        
        # Save xml
        with open(xmlFile1, 'wt') as f:
            f.write(xmlString1)
        
        # Convert xml2ebml
        with open(ebmlFile2, 'wb') as out:
            xml2ebml(xmlFile1, out, schema)
            
        # write the second xml file            
        ebmlDoc2 = schema.load(ebmlFile2, headers=True)        
        mkvRoot2 = toXml(ebmlDoc2)
        xmlString2 = ET.tostring(mkvRoot2, encoding='UTF-8')        
        with open(xmlFile2, 'wt') as f:
            f.write(xmlString2)
        
        # Load back the XML files in order to compare the two
        xmlDoc1 = loadXml(xmlFile1, schema)
        xmlDoc2 = loadXml(xmlFile2, schema)
        
        # Compare each element from the XML
        xmlEls1 = [xmlDoc1]
        xmlEls2 = [xmlDoc2]        
        while len(xmlEls1) > 0:
            self.assertEqual(xmlEls1[0], xmlEls2[0], 'Element ' \
                                                   + repr(xmlEls1[0]) \
                                                   + ' was not converted properly')
            for x in xmlEls1.pop(0).children.values():
                if issubclass(x, Element):
                    xmlEls1.append(x)
            for x in xmlEls2.pop(0).children.values():
                if issubclass(x, Element):
                    xmlEls2.append(x)            
    
    
    
    def testIde(self):
        schemaFile = '.\\schemata\\mide.xml'
        ebmlFile1 = '.\\testFiles\\SSX46714-doesnot.IDE'
        ebmlFile2 = '.\\testFiles\\SSX46714-new.IDE'
        xmlFile1 = '.\\testFiles\\ssx-1.xml'
        xmlFile2 = '.\\testFiles\\ssx-2.xml'
        
        schema = core.loadSchema(schemaFile)
        
        # Start with toXml
        ebmlDoc1 = schema.load(ebmlFile1, headers=True)
        ebmlRoot = toXml(ebmlDoc1)
        xmlString1 = ET.tostring(ebmlRoot, encoding='UTF-8')
        
        # Save xml
        with open(xmlFile1, 'wt') as f:
            f.write(xmlString1)
        
        # Convert xml2ebml
        with open(ebmlFile2, 'wb') as out:
            xml2ebml(xmlFile1, out, schema)
            
        # write the second xml file            
        ebmlDoc2 = schema.load(ebmlFile2, headers=True)        
        mkvRoot2 = toXml(ebmlDoc2)
        xmlString2 = ET.tostring(mkvRoot2, encoding='UTF-8')        
        with open(xmlFile2, 'wt') as f:
            f.write(xmlString2)
        
        # Load back the XML files in order to compare the two
        xmlDoc1 = loadXml(xmlFile1, schema)
        xmlDoc2 = loadXml(xmlFile2, schema)
        
        # Compare each element from the XML
        xmlEls1 = [xmlDoc1]
        xmlEls2 = [xmlDoc2]        
        while len(xmlEls1) > 0:
            self.assertEqual(xmlEls1[0], xmlEls2[0], 'Element ' \
                                                   + repr(xmlEls1[0]) \
                                                   + ' was not converted properly')
            for x in xmlEls1.pop(0).children.values():
                if issubclass(x, Element):
                    xmlEls1.append(x)
            for x in xmlEls2.pop(0).children.values():
                if issubclass(x, Element):
                    xmlEls2.append(x)      
                    
                    
                    
    def testPPrint(self):
        schemaFile = '.\\schemata\\mide.xml'
        schema = core.loadSchema(schemaFile)
        
        ebmlDoc = schema.load('.\\testFiles\\SSX46714-doesnot.IDE', headers=True)
        
        pprint(ebmlDoc, out=open('.\\testFiles\\IDE-Pretty.txt', 'wt'))
        xmlString = ET.tostring(toXml(ebmlDoc))
        prettyXmlFile = open('.\\testFiles\\IDE-Pretty.xml', 'wt')
        parseString(xmlString).writexml(prettyXmlFile, \
                                        addindent='\t', \
                                        newl='\n', \
                                        encoding='utf-8')
        # pprint(toXml(ebmlDoc), out=open('.\\testFiles\\IDE-Pretty.xml', 'wt'))
                
                
                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)