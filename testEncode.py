import unittest
import core
import os, sys
import collections
import types

import numpy as np

from datetime import datetime, timedelta
from difflib  import ndiff
from core     import *
from decoding import *
from encoding import *
from mock     import *
from numpy    import inf
from util     import *
from tests    import MockStream



class testEncoding(unittest.TestCase):
        
    
    def testUInt(self):
        # Test converting unsigned ints to bytes
        
        # chars
        for i in range(1, 255):
            self.assertEqual(encodeUInt(i), chr(i), \
                             'Character \'' + chr(i) + '\' not encoded properly')
            
        # uint16
        for i in range(1, 255):
            self.assertEqual(encodeUInt((i<<8) + 0x41), chr(i) + 'A', \
                             'Character \'' + chr(i)  + '\' not encoded properly')
            
        # uint32
        for i in range(1, 255):
            self.assertEqual(encodeUInt((i<<24) + 0x414141), chr(i) + 'AAA', \
                             'Character \'' + chr(i)  + '\' not encoded properly')
            
        # uint64
        for i in range(1, 255):
            self.assertEqual(encodeUInt((i<<56) + 0x41414141414141), chr(i) + 'AAAAAAA', \
                             'Character \'' + chr(i)  + '\' not encoded properly')
            
    
    
    def testInt(self):
        # Test converting signed integers into bytes
        
        # chars
        for i in range(-127, -1):
            self.assertEqual(encodeInt(i), chr(255 + i + 1), \
                             'Character \'' + chr(255 + i + 1) + '\' not encoded properly')
            
        # int16
        for i in range(-127, -1):
            self.assertEqual(encodeInt((i<<8) + 0x41), chr(255 + i + 1) + 'A', \
                             'Character \'' + chr(255 + i + 1)  + '\' not encoded properly')
            
        # int32
        for i in range(-127, -1):
            self.assertEqual(encodeInt((i<<24) + 0x414141), chr(255 + i + 1) + 'AAA', \
                             'Character \'' + chr(255 + i + 1)  + '\' not encoded properly')
            
        # int64
        for i in range(-127, -1):
            self.assertEqual(encodeInt((i<<56) + 0x41414141414141), chr(255 + i + 1) + 'AAAAAAA', \
                             'Character \'' + chr(255 + i + 1)  + '\' not encoded properly')
        
           
     
    def testFloat(self):
        # Test converting floats into bytes
        
        # empty float
        self.assertEqual(encodeFloat(10, length=0), '', 'Empty float did not return an empty string')
        
        # four byte float
        fl1 = encodeFloat(0,     length=4)
        fl2 = encodeFloat(1,     length=4)
        fl3 = encodeFloat(-2,    length=4)
        fl4 = encodeFloat(1.0/3, length=4)
        fl5 = encodeFloat(inf,   length=4)
        
        target1 = '\x00\x00\x00\x00'
        target2 = '\x3f\x80\x00\x00'
        target3 = '\xc0\x00\x00\x00'
        target4 = '\x3e\xaa\xaa\xab'
        target5 = '\x7f\x80\x00\x00'
        
        self.assertEqual(fl1, target1, '4-byte zero float not correct')        
        self.assertEqual(fl2, target2, '4-byte 1 float not correct')        
        self.assertEqual(fl3, target3, '4-byte -2 float not correct')        
        self.assertEqual(fl4, target4, '4-byte 1/3 float not correct')        
        self.assertEqual(fl5, target5, '4-byte inf float not correct')
        
        # eight byte float
        fl6  = encodeFloat(0,     length=8)
        fl7  = encodeFloat(1,     length=8)
        fl8  = encodeFloat(-2,    length=8)
        fl9  = encodeFloat(1.0/3, length=8)
        fl10 = encodeFloat(inf,   length=8)
        
        target6 =  '\x00\x00\x00\x00\x00\x00\x00\x00'
        target7 =  '\x3f\xf0\x00\x00\x00\x00\x00\x00'
        target8 =  '\xc0\x00\x00\x00\x00\x00\x00\x00'
        target9 =  '\x3f\xd5\x55\x55\x55\x55\x55\x55'
        target10 = '\x7f\xf0\x00\x00\x00\x00\x00\x00'
        
        self.assertEqual(fl6,  target6,  '8-byte zero float not correct')        
        self.assertEqual(fl7,  target7,  '8-byte 1 float not correct')        
        self.assertEqual(fl8,  target8,  '8-byte -2 float not correct')        
        self.assertEqual(fl9,  target9,  '8-byte 1/3 float not correct')        
        self.assertEqual(fl10, target10, '8-byte inf float not correct')
        

    
    def testBinary(self):
        # Test converting bytes (strings) to bytes
        
        for s in ['', 'test', 'a']:
            self.assertEqual(encodeBinary(s),          str(s))
            self.assertEqual(encodeBinary(unicode(s)), str(s))



    def testString(self):
        # Test converting strings to bytes
        
        for s in ['', 'test', 'a']:
            self.assertEqual(encodeString(s), str(s), \
                             'String not encoded as string correctly')
            
            if len(s) == 0:
                self.assertEqual(encodeString(str(s), length=2), str(s + '\x00\x00'))
            elif len(s) == 1:
                self.assertEqual(encodeString(str(s), length=2), str(s + '\x00'))
            else:
                self.assertEqual(encodeString(str(s), length=2), str(s[:2]))
                
                
                
    def testUnicode(self):
        # Test converting unicode strings to bytes
        
        for s in ['', 'test', 'a']:
            self.assertEqual(encodeString(unicode(s)), str(s), \
                             'Unicode not encoded as string correctly')
            
            if len(s) == 0:
                self.assertEqual(encodeString(unicode(s), length=2), str(s + '\x00\x00'))
            elif len(s) == 1:
                self.assertEqual(encodeString(unicode(s), length=2), str(s + '\x00'))
            else:
                self.assertEqual(encodeString(unicode(s), length=2), str(s[:2]))
                
                
    
    def testDate(self):
        # Test converting dates to bytes
        
        zeroTime = datetime.datetime(2001, 1, 1, tzinfo=None)
        delta = timedelta(microseconds=0x41425344//1000)

        self.assertEqual(encodeDate(zeroTime + delta), '\x00\x00\x00\x00ABPh')