'''
Created on Aug 14, 2017

@author: dstokes
'''
import unittest
import core
import os, sys
import numpy as np
from datetime import datetime, timedelta

from decoding import *
from encoding import *
from mock     import *
from numpy    import inf
from util     import *

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass
class testDecoding(unittest.TestCase):
    
    def setUp(self):
        
        class mockStream(object):
            
            def __init__(self):
                self.string = ''
            
            def read(self, n=None):
                if n is None:
                    n = len(self.string)
                retVal = self.string[:n]
                self.string = self.string[n:]
                return retVal
        
        self.mockStream = mockStream()
        
    
    def testDecodeIntLen(self):
        # Test getting the number of bytes in an element's size from the first
        # byte of the size
        
        for i in range(1, 255):
            self.assertEqual(decodeIntLength(i), \
                             (np.ceil(8 - np.log2(i)), i - 2**np.floor(np.log2(i)) ))
            
            
    
    def testIDLen(self):
        # Test getting the number of bytes in an ID from the first byte of the ID
        
        for i in range(16, 255):
            self.assertEqual((np.ceil(8-np.log2(i)), i), decodeIDLength(i))


    
    def testReadElID(self):
        # Test reading the ID of an element
        
        idBytes = ['\x80', \
                   '\x40\x41', \
                   '\x20\x41\x42', \
                   '\x10\x41\x42\x43']
        eIDs = [128, 16449, 2113858, 272712259]
                           
        for id, i, eID in zip(idBytes, range(1, len(idBytes) + 1), eIDs):
            self.mockStream.string = id
            readElIDOut = readElementID(self.mockStream)
            self.assertEqual(readElIDOut, (eID, i))


    
    def testReadElSize(self):
        # Test reading the size of an element
        
        idBytes = ['\x85', \
                   '\x45\x41', \
                   '\x25\x41\x42', \
                   '\x15\x41\x42\x43', \
                   '\x08\x41\x42\x43\x44', \
                   '\x04\x41\x42\x43\x44\x45', \
                   '\x02\x41\x42\x43\x44\x45\x46', \
                   '\x01\x41\x42\x43\x44\x45\x46\x47']
        elSizes = [0x5, \
                   0x541, \
                   0x54142, \
                   0x5414243, \
                   0x41424344, \
                   0x4142434445, \
                   0x414243444546, \
                   0x41424344454647]
        
        for id, i, elSz in zip(idBytes, range(1, len(idBytes) + 1), elSizes):
            self.mockStream.string = id
            self.assertEqual(readElementSize(self.mockStream), (elSz, i))
       

    
    def testReadUInt(self):
        # Test reading unsigned integers
        
        idBytes = ['\x85', \
                   '\x45\x41', \
                   '\x25\x41\x42', \
                   '\x15\x41\x42\x43']
        ints = [0x85, 0x4541, 0x254142, 0x15414243]
        
        for id, i, numOut in zip(idBytes, range(1, len(idBytes) + 1), ints):
            self.mockStream.string = id
            a = readUInt(self.mockStream, i)
            self.assertEquals(a, numOut)
       

    
    def testReadInt(self):
        # Test reading signed integers
        
        # Positive ints
        idBytes = ['\x75', \
                   '\x45\x41', \
                   '\x25\x41\x42', \
                   '\x15\x41\x42\x43']
        ints = [0x75, 0x4541, 0x254142, 0x15414243]
        
        for id, i, numOut in zip(idBytes, range(1, len(idBytes) + 1), ints):
            self.mockStream.string = id
            a = readInt(self.mockStream, i)
            self.assertEquals(a, numOut)
            
        # Negative ints
        idBytes = ['\xf5', \
                   '\xc5\x41', \
                   '\xb5\x41\x42', \
                   '\xa5\x41\x42\x43']
        ints = [-1*(0xff ^ 0xf5) - 1, \
                -1*(0xffff ^ 0xc541) - 1, \
                -1*(0xffffff ^ 0xb54142) - 1, \
                -1*(0xffffffff ^ 0xa5414243) - 1]
        
        for id, i, numOut in zip(idBytes, range(1, len(idBytes) + 1), ints):
            self.mockStream.string = id
            a = readInt(self.mockStream, i)
            self.assertEquals(a, numOut)
            
        
            
    def testReadFloat(self):
        # Test reading floating point numbers
        
        # 0 length
        self.mockStream.string = ''
        self.assertEqual(readFloat(self.mockStream, 0), 0.0)
        
        # 4-bit length
        self.mockStream.string = '\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 4), 0.0)
        
        self.mockStream.string = '\x3f\x80\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 4), 1.0)
        
        self.mockStream.string = '\xc0\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 4), -2.0)
        
        self.mockStream.string = '\x3e\xaa\xaa\xab'
        self.assertEqual(np.float32(readFloat(self.mockStream, 4)), np.float32(1.0/3.0))
    
        # 8-bit length
        self.mockStream.string = '\x00\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 8), 0.0)
        
        self.mockStream.string = '\x3f\xf0\x00\x00\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 8), 1.0)
        
        self.mockStream.string = '\xc0\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual(readFloat(self.mockStream, 8), -2.0)
        
        self.mockStream.string = '\x3f\xd5\x55\x55\x55\x55\x55\x55'
        self.assertEqual(readFloat(self.mockStream, 8), 1.0/3.0)
    
    
    
    def testReadString(self):
        # Test reading strings
        
        self.mockStream.string = ''
        self.assertEqual(readString(self.mockStream, 0), '')
        
        self.mockStream.string = 'test'
        self.assertEqual(readString(self.mockStream, len(self.mockStream.string)), \
                         'test')
            
    
    
    def testReadUnicode(self):
        # Test reading unicode strings
        
        self.mockStream.string = u''
        self.assertEqual(readUnicode(self.mockStream, 0), u'')
        
        self.mockStream.string = 'TEST'
        self.assertEqual(readUnicode(self.mockStream, len(self.mockStream.string)), \
                         u'TEST')
    
    
    
    def testReadDate(self):
        # Test reading dates from bytes
        
        self.mockStream.string = '\x00\x00\x00\x00ABCD'
        a = readDate(self.mockStream)
        self.assertEqual(a, datetime.datetime(2001, 1, 1, tzinfo=None) + \
                            timedelta(microseconds=0x41424344//1000))
        
    
    
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
                
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()