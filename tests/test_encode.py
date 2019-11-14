import unittest
from datetime import timedelta, datetime
import sys

from ebmlite.encoding import encodeBinary, encodeDate, encodeFloat, encodeInt, \
    encodeString, encodeUInt


def as_unicode(s):
    if sys.version_info.major >= 3:
        return s
    else:
        return unicode(s, 'latin-1')


class testEncoding(unittest.TestCase):
    """ Unit tests for ebmlite.encoding"""
        
    
    def testUInt(self):
        """ Test converting unsigned ints to bytes. """

        # General cases
        #   chars
        for i in range(0, 256):
            self.assertEqual(encodeUInt(i, length=1), as_unicode(chr(i)),
                             'Character %X not encoded properly' % i)
            
        #   uint16
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i<<8) + 0x41, length=2), as_unicode(chr(i) + 'A'),
                             'Character %X not encoded properly' % i)
            
        #   uint32
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i<<24) + 0x414141, length=4), as_unicode(chr(i) + 'AAA'),
                             "Character %X not encoded properly" % i)
            
        #   uint64
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i<<56) + 0x41414141414141, length=8), as_unicode(chr(i) + 'AAAAAAA'),
                             'Character %X not encoded properly' % i)

        # Length paramater behavior
        #   unspecified length calls should truncate to smallest length possible
        self.assertEqual(encodeUInt(0x123), u'\x01\x23')
        #   which for zero is an empty string
        self.assertEqual(encodeUInt(0), u'')
        
        #   specified length should pad to given length for all values
        self.assertEqual(encodeUInt(0x123, length=3), u'\x00\x01\x23')
        #   and specifying a length that's too small should result in a ValueError
        with self.assertRaises(ValueError):
            encodeUInt(0x123, length=1)



    def testInt(self):
        """ Test converting signed integers into bytes. """

        # General cases
        #   chars
        for i in range(-128, 128):
            self.assertEqual(encodeInt(i, length=1), as_unicode(chr(i % 256)),
                             'Character %X  not encoded properly' % (i % 256))
            
        #   int16
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i<<8) + 0x41, length=2), as_unicode(chr(i % 256) + 'A'),
                             'Character %X  not encoded properly' % (i % 256))
            
        #   int32
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i<<24) + 0x414141, length=4), as_unicode(chr(i % 256) + 'AAA'),
                             'Character %X  not encoded properly' % (i % 256))
            
        #   int64
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i<<56) + 0x41414141414141, length=8), as_unicode(chr(i % 256) + 'AAAAAAA'),
                             'Character %X  not encoded properly' % (i % 256))

        # Length paramater behavior
        #   unspecified length calls should truncate to smallest length possible
        self.assertEqual(encodeInt(0x123), u'\x01\x23')
        self.assertEqual(encodeInt(-0x123), u'\xfe\xdd')
        #   which for zero is an empty string
        self.assertEqual(encodeInt(0), u'')
        self.assertEqual(encodeInt(-1), u'\xff')
        
        #   specified length should pad to given length for all values
        self.assertEqual(encodeInt(0x123, length=3), u'\x00\x01\x23')
        self.assertEqual(encodeInt(-0x123, length=3), u'\xff\xfe\xdd')
        #   and specifying a length that's too small should result in a ValueError
        with self.assertRaises(ValueError):
            encodeInt(0x123, length=1)
        with self.assertRaises(ValueError):
            encodeInt(-0x123, length=1)
        with self.assertRaises(ValueError):
            encodeInt(-1, length=0)


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
