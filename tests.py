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
        file = '.\\testFiles\\video-1.mkv'
        schema = core.loadSchema('.\\schemata\\matroska.xml')
        
        # Start with toXml
        doc = schema.load(file, headers=True)
        mkvRoot = toXml(doc)
        s = ET.tostring(mkvRoot, encoding='UTF-8')
        
        # Save xml
        with open('.\\testFiles\\video-1.xml', 'wt') as f:
            f.write(s)
        
        # Convert xml2ebml
        with open('.\\testFiles\\video-2.mkv', 'wb') as out:
            xml2ebml('.\\testFiles\\video-1.xml', out, schema)
            
            
        doc2 = schema.load('.\\testFiles\\video-2.mkv', headers=True)
        mkvRoot2 = toXml(doc2)
        s2 = ET.tostring(mkvRoot2, encoding='UTF-8')
        
        with open('.\\testFiles\\video-2.xml', 'wt') as f:
            f.write(s2)
    
    
    def testIde(self):
        file = '.\\testFiles\\SSX46714-doesnot.IDE'
        ideXml = toXml(core.loadSchema('.\\schemata\\mide.xml').load(file))
        ideName = os.path.split(ideXml.attrib['source'])[1]
        nonData = [e for e in ideXml.getchildren() if e.tag != 'ChannelDataBlock']
        
        ideString = ET.tostring(ideXml, encoding='utf-8')
        
        nonDataEls = [el for el in ideXml if el.tag != 'ChannelDataBlock']
        
        self.assertEqual(nonDataEls[0].tag, 'RecordingProperties', 'Recording ' \
                         + 'properties not present in IDE file')
                
                
                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)