import unittest
from datetime import timedelta, datetime
import sys

from ebmlite.encoding import encodeBinary, encodeDate, encodeFloat, encodeInt, \
    encodeString, encodeUInt



class testEncoding(unittest.TestCase):
    """ Unit tests for ebmlite.encoding"""
        
    
    def testUInt(self):
        """ Test converting unsigned ints to bytes. """

        if sys.version_info.major == 3:
            # chars
            for i in range(1, 255):
                val = encodeUInt(i)
                target = chr(i)
                self.assertEqual(val, target,
                                 'Character %X not encoded properly' % i)

            # uint16
            for i in range(1, 255):
                self.assertEqual(encodeUInt((i<<8) + 0x41), chr(i) + u'A',
                                 'Character %X not encoded properly' % i)

            # uint32
            for i in range(1, 255):
                self.assertEqual(encodeUInt((i<<24) + 0x414141), chr(i) + u'AAA',
                                 "Character %X not encoded properly" % i)

            # uint64
            for i in range(1, 255):
                self.assertEqual(encodeUInt((i<<56) + 0x41414141414141), chr(i) + u'AAAAAAA',
                                 'Character %X not encoded properly' % i)
        else:
            # chars
            for i in range(1, 255):
                val = encodeUInt(i)
                target = chr(i)
                self.assertEqual(val, unicode(target, 'latin-1'),
                                 b'Character %X not encoded properly' % i)

            # uint16
            for i in range(1, 255):
                self.assertEqual(encodeUInt((i<<8) + 0x41), unicode(chr(i) + b'A', 'latin-1'),
                                 'Character %X not encoded properly' % i)

            # uint32
            for i in range(1, 255):
                self.assertEqual(encodeUInt((i<<24) + 0x414141), unicode(chr(i) + b'AAA', 'latin-1'),
                                 "Character %X not encoded properly" % i)

            # uint64
            for i in range(1, 255):
                self.assertEqual(encodeUInt((i<<56) + 0x41414141414141), unicode(chr(i) + b'AAAAAAA', 'latin-1'),
                                 'Character %X not encoded properly' % i)
    
    
    def testInt(self):
        """ Test converting signed integers into bytes. """

        if sys.version_info.major == 3:
            # chars
            for i in range(-127, -1):
                self.assertEqual(encodeInt(i), chr(255 + i + 1),
                                 'Character %X  not encoded properly' % (255 + i + 1))

            # int16
            for i in range(-127, -1):
                self.assertEqual(encodeInt((i << 8) + 0x41), chr(255 + i + 1) + u'A',
                                 'Character %X  not encoded properly' % (255 + i + 1))

            # int32
            for i in range(-127, -1):
                self.assertEqual(encodeInt((i << 24) + 0x414141), chr(255 + i + 1) + u'AAA',
                                 'Character %X  not encoded properly' % (255 + i + 1))

            # int64
            for i in range(-127, -1):
                self.assertEqual(encodeInt((i << 56) + 0x41414141414141),
                                 chr(255 + i + 1) + u'AAAAAAA',
                                 'Character %X  not encoded properly' % (255 + i + 1))
        else:
            # chars
            for i in range(-127, -1):
                self.assertEqual(encodeInt(i), unicode(chr(255 + i + 1), 'latin-1'),
                                 'Character %X  not encoded properly' % (255 + i + 1))

            # int16
            for i in range(-127, -1):
                self.assertEqual(encodeInt((i<<8) + 0x41), unicode(chr(255 + i + 1) + b'A', 'latin-1'),
                                 'Character %X  not encoded properly' % (255 + i + 1))

            # int32
            for i in range(-127, -1):
                self.assertEqual(encodeInt((i<<24) + 0x414141), unicode(chr(255 + i + 1) + b'AAA', 'latin-1'),
                                 'Character %X  not encoded properly' % (255 + i + 1))

            # int64
            for i in range(-127, -1):
                self.assertEqual(encodeInt((i<<56) + 0x41414141414141), unicode(chr(255 + i + 1) + b'AAAAAAA', 'latin-1'),
                                 'Character %X  not encoded properly' % (255 + i + 1))
        
           
     
    def testFloat(self):
        """ Test converting floats into bytes. """
        
        # empty float
        self.assertEqual(encodeFloat(10, length=0), u'', 'Empty float did not return an empty string')
        
        # four byte float
        fl1 = encodeFloat(0,            length=4)
        fl2 = encodeFloat(1,            length=4)
        fl3 = encodeFloat(-2,           length=4)
        fl4 = encodeFloat(1.0/3,        length=4)
        fl5 = encodeFloat(float('Inf'), length=4)
        
        target1 = u'\x00\x00\x00\x00'
        target2 = u'\x3f\x80\x00\x00'
        target3 = u'\xc0\x00\x00\x00'
        target4 = u'\x3e\xaa\xaa\xab'
        target5 = u'\x7f\x80\x00\x00'
        
        self.assertEqual(fl1, target1, '4-byte zero float not correct')        
        self.assertEqual(fl2, target2, '4-byte 1 float not correct')        
        self.assertEqual(fl3, target3, '4-byte -2 float not correct')        
        self.assertEqual(fl4, target4, '4-byte 1/3 float not correct')        
        self.assertEqual(fl5, target5, '4-byte inf float not correct')
        
        # eight byte float
        fl6  = encodeFloat(0,            length=8)
        fl7  = encodeFloat(1,            length=8)
        fl8  = encodeFloat(-2,           length=8)
        fl9  = encodeFloat(1.0/3,        length=8)
        fl10 = encodeFloat(float('Inf'), length=8)
        
        target6 =  u'\x00\x00\x00\x00\x00\x00\x00\x00'
        target7 =  u'\x3f\xf0\x00\x00\x00\x00\x00\x00'
        target8 =  u'\xc0\x00\x00\x00\x00\x00\x00\x00'
        target9 =  u'\x3f\xd5\x55\x55\x55\x55\x55\x55'
        target10 = u'\x7f\xf0\x00\x00\x00\x00\x00\x00'
        
        self.assertEqual(fl6,  target6,  '8-byte zero float not correct')        
        self.assertEqual(fl7,  target7,  '8-byte 1 float not correct')        
        self.assertEqual(fl8,  target8,  '8-byte -2 float not correct')        
        self.assertEqual(fl9,  target9,  '8-byte 1/3 float not correct')        
        self.assertEqual(fl10, target10, '8-byte inf float not correct')

    def testBinary(self):
        """ Test converting bytes (strings) to bytes. """
        
        for s in [u'', u'test', u'a']:
            if sys.version_info.major == 3:
                self.assertEqual(encodeBinary(s), s)
            else:
                self.assertEqual(encodeBinary(s),          s)
                self.assertEqual(encodeBinary(unicode(s)), s)



    def testString(self):
        """ Test converting strings to bytes. """
        
        for s in [u'', u'test', u'a']:
            self.assertEqual(encodeString(s), s,
                             'String not encoded as string correctly')
            
            if len(s) == 0:
                self.assertEqual(encodeString(s, length=2), s + u'\x00\x00')
            elif len(s) == 1:
                self.assertEqual(encodeString(s, length=2), s + u'\x00')
            else:
                self.assertEqual(encodeString(s, length=2), s[:2])
                
                
                
    def testUnicode(self):
        """ Test converting unicode strings to bytes. """

        for s in [u'', u'test', u'a']:
            self.assertEqual(encodeString(s), s,
                             'Unicode not encoded as string correctly')

            if len(s) == 0:
                self.assertEqual(encodeString(s, length=2), (s + '\x00\x00'))
            elif len(s) == 1:
                self.assertEqual(encodeString(s, length=2), (s + '\x00'))
            else:
                self.assertEqual(encodeString(s, length=2), s[:2])
                
                
    
    def testDate(self):
        """ Test converting dates to bytes. """
        
        zeroTime = datetime(2001, 1, 1, tzinfo=None)
        delta = timedelta(microseconds=0x41425344//1000)

        self.assertEqual(encodeDate(zeroTime + delta), u'\x00\x00\x00\x00ABPh')