import unittest
from datetime import timedelta, datetime

from ebmlite.encoding import encodeBinary, encodeDate, encodeFloat, encodeInt, \
    encodeString, encodeUInt



class testEncoding(unittest.TestCase):
    """ Unit tests for ebmlite.encoding"""
        
    
    def testUInt(self):
        """ Test converting unsigned ints to bytes. """

        # General cases
        #   chars
        for i in range(0, 256):
            self.assertEqual(encodeUInt(i, length=1), chr(i).encode('latin-1'),
                             b'Character %X not encoded properly' % i)
            
        #   uint16
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i<<8) + 0x41, length=2), chr(i).encode('latin-1') + b'A',
                             b'Character %X not encoded properly' % i)
            
        #   uint32
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i<<24) + 0x414141, length=4), chr(i).encode('latin-1') + b'AAA',
                             b"Character %X not encoded properly" % i)
            
        #   uint64
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i<<56) + 0x41414141414141, length=8), chr(i).encode('latin-1') + b'AAAAAAA',
                             b'Character %X not encoded properly' % i)

        # Length paramater behavior
        #   unspecified length calls should truncate to smallest length possible
        self.assertEqual(encodeUInt(0x123), b'\x01\x23')
        #   which for zero is an empty string
        self.assertEqual(encodeUInt(0), b'')
        
        #   specified length should pad to given length for all values
        self.assertEqual(encodeUInt(0x123, length=3), b'\x00\x01\x23')
        #   and specifying a length that's too small should result in a ValueError
        with self.assertRaises(ValueError):
            encodeUInt(0x123, length=1)



    def testInt(self):
        """ Test converting signed integers into bytes. """

        # General cases
        #   chars
        for i in range(-128, 128):
            self.assertEqual(encodeInt(i, length=1), chr(i % 256).encode('latin-1'),
                             b'Character %X  not encoded properly' % (i % 256))
            
        #   int16
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i<<8) + 0x41, length=2), chr(i % 256).encode('latin-1') + b'A',
                             b'Character %X  not encoded properly' % (i % 256))
            
        #   int32
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i<<24) + 0x414141, length=4), chr(i % 256).encode('latin-1') + b'AAA',
                             b'Character %X  not encoded properly' % (i % 256))
            
        #   int64
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i<<56) + 0x41414141414141, length=8), chr(i % 256).encode('latin-1') + b'AAAAAAA',
                             b'Character %X  not encoded properly' % (i % 256))

        # Length paramater behavior
        #   unspecified length calls should truncate to smallest length possible
        self.assertEqual(encodeInt(0x123), b'\x01\x23')
        self.assertEqual(encodeInt(-0x123), b'\xfe\xdd')
        #   which for zero is an empty string
        self.assertEqual(encodeInt(0), b'')
        self.assertEqual(encodeInt(-1), b'\xff')
        
        #   specified length should pad to given length for all values
        self.assertEqual(encodeInt(0x123, length=3), b'\x00\x01\x23')
        self.assertEqual(encodeInt(-0x123, length=3), b'\xff\xfe\xdd')
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
        self.assertEqual(encodeFloat(10, length=0), b'', b'Empty float did not return an empty string')
        
        # four byte float
        fl1 = encodeFloat(0,            length=4)
        fl2 = encodeFloat(1,            length=4)
        fl3 = encodeFloat(-2,           length=4)
        fl4 = encodeFloat(1.0/3,        length=4)
        fl5 = encodeFloat(float(b'Inf'), length=4)
        
        target1 = b'\x00\x00\x00\x00'
        target2 = b'\x3f\x80\x00\x00'
        target3 = b'\xc0\x00\x00\x00'
        target4 = b'\x3e\xaa\xaa\xab'
        target5 = b'\x7f\x80\x00\x00'
        
        self.assertEqual(fl1, target1, b'4-byte zero float not correct')
        self.assertEqual(fl2, target2, b'4-byte 1 float not correct')
        self.assertEqual(fl3, target3, b'4-byte -2 float not correct')
        self.assertEqual(fl4, target4, b'4-byte 1/3 float not correct')
        self.assertEqual(fl5, target5, b'4-byte inf float not correct')
        
        # eight byte float
        fl6  = encodeFloat(0,            length=8)
        fl7  = encodeFloat(1,            length=8)
        fl8  = encodeFloat(-2,           length=8)
        fl9  = encodeFloat(1.0/3,        length=8)
        fl10 = encodeFloat(float(b'Inf'), length=8)
        
        target6 =  b'\x00\x00\x00\x00\x00\x00\x00\x00'
        target7 =  b'\x3f\xf0\x00\x00\x00\x00\x00\x00'
        target8 =  b'\xc0\x00\x00\x00\x00\x00\x00\x00'
        target9 =  b'\x3f\xd5\x55\x55\x55\x55\x55\x55'
        target10 = b'\x7f\xf0\x00\x00\x00\x00\x00\x00'
        
        self.assertEqual(fl6,  target6,  b'8-byte zero float not correct')
        self.assertEqual(fl7,  target7,  b'8-byte 1 float not correct')
        self.assertEqual(fl8,  target8,  b'8-byte -2 float not correct')
        self.assertEqual(fl9,  target9,  b'8-byte 1/3 float not correct')
        self.assertEqual(fl10, target10, b'8-byte inf float not correct')
        

    
    def testBinary(self):
        """ Test converting bytes (strings) to bytes. """
        
        for s in [b'', b'test', b'a']:
            self.assertEqual(encodeBinary(s),          bytes(s))
            self.assertEqual(encodeBinary(bytes(s)), bytes(s))



    def testString(self):
        """ Test converting strings to bytes. """
        
        for s in [b'', b'test', b'a']:
            self.assertEqual(encodeString(s), s,
                             b'String not encoded as string correctly')
            
            if len(s) == 0:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00\x00'))
            elif len(s) == 1:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00'))
            else:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s[:2]))
                
                
                
    def testUnicode(self):
        """ Test converting unicode strings to bytes. """
        
        for s in [b'', b'test', b'a']:
            self.assertEqual(encodeString(bytes(s)), bytes(s),
                             b'Unicode not encoded as string correctly')
            
            if len(s) == 0:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00\x00'))
            elif len(s) == 1:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00'))
            else:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s[:2]))
                
                
    
    def testDate(self):
        """ Test converting dates to bytes. """
        
        zeroTime = datetime(2001, 1, 1, tzinfo=None)
        delta = timedelta(microseconds=0x41425344//1000)

        self.assertEqual(encodeDate(zeroTime + delta), b'\x00\x00\x00\x00ABPh')