import unittest
from datetime import timedelta, datetime

from ebmlite.encoding import getLength, encodeBinary, encodeDate, encodeFloat, \
    encodeInt, encodeString, encodeUInt, encodeSize, encodeId, encodeUnicode


class testUtilFunctions(unittest.TestCase):

    def testGetLength(self):
        for i in range(100):
            val = 2**i
            actual = getLength(val)
            correct = 0
            while True:
                if val > (2**(7*correct) - 2):
                    correct += 1
                else:
                    break

            correct = min(correct, 8)

            self.assertEqual(correct, actual)

    def testEncodeSize(self):
        val1 = encodeSize(1)
        val2 = encodeSize(100)
        val3 = encodeSize(1000)
        val4 = encodeSize(2**60)

        expected1 = bytes([0b10000001])
        expected2 = bytes([0b11100100])
        expected3 = bytes([0b01000011, 0b11101000])
        expected4 = bytes([0b00010001, 0b00000000, 0b00000000, 0b00000000,
                           0b00000000, 0b00000000, 0b00000000, 0b00000000])

        self.assertEqual(expected1, val1, 'failed to encode 1')
        self.assertEqual(expected2, val2, 'failed to encode 100')
        self.assertEqual(expected3, val3, 'failed to encode 1000')
        self.assertEqual(expected4, val4, 'failed to encode 2**60')

    def testEncodeSizeLong(self):
        val1 = encodeSize(1, 4)
        val2 = encodeSize(100, 4)
        val3 = encodeSize(1000, 4)
        val4 = encodeSize(None, length=4)

        expected1 = bytes([0b00010000, 0b00000000, 0b00000000, 0b00000001])
        expected2 = bytes([0b00010000, 0b00000000, 0b00000000, 0b01100100])
        expected3 = bytes([0b00010000, 0b00000000, 0b00000011, 0b11101000])
        expected4 = bytes([0b11111111]*4)

        self.assertEqual(expected1, val1, 'failed to encode 1')
        self.assertEqual(expected2, val2, 'failed to encode 100')
        self.assertEqual(expected3, val3, 'failed to encode 1000')
        self.assertEqual(expected4, val4, 'failed to encode None')

    def testBadSize(self):
        with self.assertRaises(ValueError):
            encodeSize(1.3)

        with self.assertRaises(ValueError):
            encodeSize(2**70)

    def testEncodeId(self):
        val1 = encodeId(1 + 128)
        val2 = encodeId(100 + 128)
        val3 = encodeId(1000 + 16384)
        val4 = encodeId(10000 + 16384)

        expected1 = bytes([0b10000001])
        expected2 = bytes([0b11100100])
        expected3 = bytes([0b01000011, 0b11101000])
        expected4 = bytes([0b01100111, 0b00010000])

        self.assertEqual(expected1, val1, 'failed to encode 1')
        self.assertEqual(expected2, val2, 'failed to encode 100')
        self.assertEqual(expected3, val3, 'failed to encode 1000')
        self.assertEqual(expected4, val4, 'failed to encode 10000')

    def testEncodeIdSize(self):
        val1 = encodeId(1 + 128, length=3)
        val2 = encodeId(100 + 128, length=3)
        val3 = encodeId(1000 + 16384, length=3)
        val4 = encodeId(10000 + 16384, length=3)

        expected1 = bytes([0b00000000, 0b00000000, 0b10000001])
        expected2 = bytes([0b00000000, 0b00000000, 0b11100100])
        expected3 = bytes([0b00000000, 0b01000011, 0b11101000])
        expected4 = bytes([0b00000000, 0b01100111, 0b00010000])

        self.assertEqual(expected1, val1, 'failed to encode 1')
        self.assertEqual(expected2, val2, 'failed to encode 100')
        self.assertEqual(expected3, val3, 'failed to encode 1000')
        self.assertEqual(expected4, val4, 'failed to encode 10000')

        with self.assertRaises(ValueError):
            encodeId(2**60, length=5)

        with self.assertRaises(ValueError):
            encodeId(2**60, length=0)

        with self.assertRaises(ValueError):
            encodeId(2**60, length=1)


class testEncoding(unittest.TestCase):
    """ Unit tests for ebmlite.encoding"""
        
    
    def testUInt(self):
        """ Test converting unsigned ints to bytes. """

        # General cases
        #   chars
        for i in range(0, 256):
            self.assertEqual(encodeUInt(i, length=1),
                             chr(i).encode('latin-1'),
                             'Character %X not encoded properly' % i)
            
        #   uint16
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i << 8) + 0x41, length=2),
                             chr(i).encode('latin-1') + b'A',
                             'Character %X not encoded properly' % i)
            
        #   uint32
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i << 24) + 0x414141, length=4),
                             chr(i).encode('latin-1') + b'AAA',
                             "Character %X not encoded properly" % i)
            
        #   uint64
        for i in range(0, 256):
            self.assertEqual(encodeUInt((i << 56) + 0x41414141414141, length=8),
                             chr(i).encode('latin-1') + b'AAAAAAA',
                             'Character %X not encoded properly' % i)

        # Length parameter behavior
        #   unspecified length calls should truncate to the smallest possible length
        self.assertEqual(encodeUInt(0x123), b'\x01\x23')
        #   but zero should still be a nonempty string
        self.assertEqual(encodeUInt(0), b'\x00')
        
        #   specified length should pad to given length for all values
        self.assertEqual(encodeUInt(0x123, length=3), b'\x00\x01\x23')
        #   and specifying a length that's too small should result in a ValueError
        with self.assertRaises(ValueError):
            encodeUInt(0x123, length=1)
        with self.assertRaises(ValueError):
            encodeUInt(0, length=0)

        with self.assertRaises(ValueError):
            encodeUInt(-42)
        with self.assertRaises(TypeError):
            encodeUInt('bogus')


    def testInt(self):
        """ Test converting signed integers into bytes. """

        # General cases
        #   chars
        for i in range(-128, 128):
            self.assertEqual(encodeInt(i, length=1),
                             chr(i % 256).encode('latin-1'),
                             'Character %X  not encoded properly' % (i % 256))
            
        #   int16
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i << 8) + 0x41, length=2),
                             chr(i % 256).encode('latin-1') + b'A',
                             'Character %X  not encoded properly' % (i % 256))
            
        #   int32
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i << 24) + 0x414141, length=4),
                             chr(i % 256).encode('latin-1') + b'AAA',
                             'Character %X  not encoded properly' % (i % 256))
            
        #   int64
        for i in range(-128, 128):
            self.assertEqual(encodeInt((i << 56) + 0x41414141414141, length=8),
                             chr(i % 256).encode('latin-1') + b'AAAAAAA',
                             'Character %X  not encoded properly' % (i % 256))

        self.assertEqual(encodeInt(0b10000000), b'\x00\x80')

        # Length parameter behavior
        #   unspecified length calls should truncate to the smallest possible length
        self.assertEqual(encodeInt(0x123), b'\x01\x23')
        self.assertEqual(encodeInt(-0x123), b'\xfe\xdd')
        #   but 0/(-1) should still be nonempty strings
        self.assertEqual(encodeInt(0), b'\x00')
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
            encodeInt(0, length=0)
        with self.assertRaises(ValueError):
            encodeInt(-1, length=0)
        # type check
        with self.assertRaises(TypeError):
            encodeInt('bogus')

    def testFloat(self):
        """ Test converting floats into bytes. """
        
        # empty float
        self.assertEqual(encodeFloat(10, length=0),
                         b'',
                         'Empty float did not return an empty string')
        
        # four byte float
        fl1 = encodeFloat(0,            length=4)
        fl2 = encodeFloat(1,            length=4)
        fl3 = encodeFloat(-2,           length=4)
        fl4 = encodeFloat(1.0/3,        length=4)
        fl5 = encodeFloat(float('Inf'), length=4)
        
        target1 = b'\x00\x00\x00\x00'
        target2 = b'\x3f\x80\x00\x00'
        target3 = b'\xc0\x00\x00\x00'
        target4 = b'\x3e\xaa\xaa\xab'
        target5 = b'\x7f\x80\x00\x00'
        
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
        
        target6 =  b'\x00\x00\x00\x00\x00\x00\x00\x00'
        target7 =  b'\x3f\xf0\x00\x00\x00\x00\x00\x00'
        target8 =  b'\xc0\x00\x00\x00\x00\x00\x00\x00'
        target9 =  b'\x3f\xd5\x55\x55\x55\x55\x55\x55'
        target10 = b'\x7f\xf0\x00\x00\x00\x00\x00\x00'
        
        self.assertEqual(fl6,  target6,  '8-byte zero float not correct')
        self.assertEqual(fl7,  target7,  '8-byte 1 float not correct')
        self.assertEqual(fl8,  target8,  '8-byte -2 float not correct')
        self.assertEqual(fl9,  target9,  '8-byte 1/3 float not correct')
        self.assertEqual(fl10, target10, '8-byte inf float not correct')

        # floats without specified length
        fl11 = encodeFloat(0)
        fl12 = encodeFloat(1)
        fl13 = encodeFloat(-2)
        fl14 = encodeFloat(1.0/3)
        fl15 = encodeFloat(float('Inf'))

        target11 = b''
        target12 = b'\x3f\xf0\x00\x00\x00\x00\x00\x00'
        target13 = b'\xc0\x00\x00\x00\x00\x00\x00\x00'
        target14 = b'\x3f\xd5\x55\x55\x55\x55\x55\x55'
        target15 = b'\x7f\xf0\x00\x00\x00\x00\x00\x00'

        self.assertEqual(fl11, target11, '8-byte zero float not correct')
        self.assertEqual(fl12, target12, '8-byte 1 float not correct')
        self.assertEqual(fl13, target13, '8-byte -2 float not correct')
        self.assertEqual(fl14, target14, '8-byte 1/3 float not correct')
        self.assertEqual(fl15, target15, '8-byte inf float not correct')
        
        with self.assertRaises(ValueError):
            encodeFloat(1.0, length=5)

        with self.assertRaises(TypeError):
            encodeFloat('bogus')

    def testBinary(self):
        """ Test converting bytes (strings) to bytes. """
        
        for s in [b'', b'test', b'a']:
            self.assertEqual(encodeBinary(s), s)

        for s in ['', 'test', 'a', 'Midé', '🐍', '🧃']:
            self.assertEqual(encodeBinary(s), s.encode('utf-8'))

        self.assertEqual(encodeBinary(None), b'')

        with self.assertRaises(TypeError):
            encodeBinary(42)

    def testBinaryLength(self):
        """ Test converting bytes (strings) to bytes. """

        for s in [b'', b'test', b'a']:
            self.assertEqual(
                    encodeBinary(s, length=20),
                    s.ljust(20, b'\x00'),
                    'failed to encode {} as bytes'.format(s))

        for s in ['', 'test', 'a', 'Midé', '🐍', '🧃']:
            self.assertEqual(
                    encodeBinary(s, length=20),
                    s.encode('utf-8').ljust(20, b'\x00'),
                    'failed to encode {} as unicode'.format(s))

        with self.assertRaises(ValueError):
            encodeBinary('🐍', length=1)

    def testString(self):
        """ Test converting strings to bytes. """
        
        for s in [b'', b'test', b'a']:
            self.assertEqual(encodeString(s), s,
                             'String not encoded as string correctly')
            
            if len(s) == 0:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00\x00'))
            elif len(s) == 1:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00'))
            else:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s[:2]))

        with self.assertRaises(TypeError):
            encodeString(42)


    def testStringWithUnicode(self):

        for s in ['', 'test', 'a', 'Midé', '🐍', '🧃']:
            s = s.encode('ascii', 'replace')
            self.assertEqual(encodeString(s), s,
                             'String not encoded as string correctly')

            if len(s) == 0:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00\x00'))
            elif len(s) == 1:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s + b'\x00'))
            else:
                self.assertEqual(encodeString(bytes(s), length=2), bytes(s[:2]))
                
    def testUnicode(self):
        """ Test converting unicode strings to bytes. """
        
        for s in ['', 'test', 'a', 'Midé', '🐍', '🧃']:
            self.assertEqual(
                    encodeUnicode(s),
                    s.encode('utf-8'),
                    'Unicode of {} not encoded as string correctly'.format(s))
        with self.assertRaises(TypeError):
            encodeUnicode(42)


    def testUnicodeLength(self):
        """ Test converting unicode strings to bytes. """

        for s in ['', 'test', 'a', 'Midé', '🐍', '🧃']:

            self.assertEqual(
                    encodeUnicode(s, length=2),
                    s.encode('utf-8').ljust(2, b'\x00')[:2])
    
    def testDate(self):
        """ Test converting dates to bytes. """
        
        zeroTime = datetime(2001, 1, 1, tzinfo=None)
        delta = timedelta(microseconds=0x41425344//1000)

        self.assertEqual(encodeDate(zeroTime + delta), b'\x00\x00\x00\x00ABPh')

        with self.assertRaises(TypeError):
            encodeDate('bogus')


    def testNow(self):
        """ Test converting dates to bytes. """
        now = datetime.utcnow()
        nowEncoded = encodeDate(None)
        delta = now - datetime(2001, 1, 1, tzinfo=None)
        self.assertEqual(
                nowEncoded[:4],
                encodeInt(int((delta.microseconds + ((delta.seconds + (delta.days*86400))*1e6))*1e3))[:4],
                )

    def testDateLength(self):
        """ Test converting dates to bytes. """

        zeroTime = datetime(2001, 1, 1, tzinfo=None)
        delta = timedelta(microseconds=0x41425344//1000)

        self.assertEqual(
                encodeDate(zeroTime + delta, length=8),
                b'\x00\x00\x00\x00ABPh',
                )

        with self.assertRaises(ValueError):
            encodeDate(zeroTime + delta, length=4)
