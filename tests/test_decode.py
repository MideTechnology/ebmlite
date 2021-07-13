import unittest
from datetime import timedelta, datetime
from math import ceil, floor, log
from io import BytesIO

from ebmlite.decoding import decodeIDLength, decodeIntLength, readDate, readElementID, \
    readElementSize, readFloat, readInt, readString, readUInt, readUnicode



class testDecoding(unittest.TestCase):
    """ Unit tests for ebmlite.decoding. """

    def setUp(self):
        
        self.mockStream = BytesIO()
        
    
    def testDecodeIntLen(self):
        """ Test getting the number of bytes in an element's size from the first
            byte of the size.
        """
        
        for i in range(1, 256):
            self.assertEqual(decodeIntLength(i),
                             (ceil(8 - log(i, 2)), i - 2**floor(log(i, 2)) ))
            
            
    
    def testIDLen(self):
        """ Test getting the number of bytes in an ID from the first byte of
            the ID.
        """
        
        for i in range(16, 256):
            self.assertEqual((ceil(8-log(i, 2)), i), decodeIDLength(i))


    
    def testReadElID(self):
        """ Test reading the ID of an element. """
        
        idBytes = [b'\x80',
                   b'\x40\x41',
                   b'\x20\x41\x42',
                   b'\x10\x41\x42\x43']
        eIDs = [128, 16449, 2113858, 272712259]
                           
        for i, (id, eID) in enumerate(zip(idBytes, eIDs)):
            self.mockStream = BytesIO(id)
            self.mockStream.seek(0)
            readElIDOut = readElementID(self.mockStream)
            self.assertEqual(readElIDOut, (eID, i + 1))


    
    def testReadElSize(self):
        """ Test reading the size of an element. """
        
        idBytes = [b'\x85',
                   b'\x45\x41',
                   b'\x25\x41\x42',
                   b'\x15\x41\x42\x43',
                   b'\x08\x41\x42\x43\x44',
                   b'\x04\x41\x42\x43\x44\x45',
                   b'\x02\x41\x42\x43\x44\x45\x46',
                   b'\x01\x41\x42\x43\x44\x45\x46\x47']
        elSizes = [0x5,
                   0x541,
                   0x54142,
                   0x5414243,
                   0x41424344,
                   0x4142434445,
                   0x414243444546,
                   0x41424344454647]
        
        for i, (id, elSz) in enumerate(zip(idBytes, elSizes)):
            self.mockStream = BytesIO(id)
            self.mockStream.seek(0)
            self.assertEqual(readElementSize(self.mockStream), (elSz, i + 1))
       

    
    def testReadUInt(self):
        """ Test reading unsigned integers. """
        
        idBytes = [b'\x85',
                   b'\x45\x41',
                   b'\x25\x41\x42',
                   b'\x15\x41\x42\x43']
        ints = [0x85, 0x4541, 0x254142, 0x15414243]

        for i, (id, numOut) in enumerate(zip(idBytes, ints)):
            self.mockStream = BytesIO(id)
            self.mockStream.seek(0)
            val = readUInt(self.mockStream, i + 1)
            self.assertEqual(val, numOut)
       

    
    def testReadInt(self):
        """ Test reading signed integers. """
        
        # Positive ints
        idBytes = [b'\x75',
                   b'\x45\x41',
                   b'\x25\x41\x42',
                   b'\x15\x41\x42\x43']
        ints = [0x75, 0x4541, 0x254142, 0x15414243]
        
        for i, (id, numOut) in enumerate(zip(idBytes, ints)):
            self.mockStream = BytesIO(id)
            val = readInt(self.mockStream, i + 1)
            self.assertEqual(val, numOut)
            
        # Negative ints
        idBytes = [b'\xf5',
                   b'\xc5\x41',
                   b'\xb5\x41\x42',
                   b'\xa5\x41\x42\x43']
        ints = [-1*(0xff ^ 0xf5) - 1,
                -1*(0xffff ^ 0xc541) - 1,
                -1*(0xffffff ^ 0xb54142) - 1,
                -1*(0xffffffff ^ 0xa5414243) - 1]
        
        for i, (id, numOut) in enumerate(zip(idBytes,  ints)):
            self.mockStream = BytesIO(id)
            val = readInt(self.mockStream, i + 1)
            self.assertEqual(val, numOut)
            
        
            
    def testReadFloat(self):
        """ Test reading floating point numbers. """
        
        # 0 length
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'')
        self.assertEqual(readFloat(self.mockStream, 0), 0.0)
        
        # 4-bit length
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\x00\x00\x00\x00')
        self.assertEqual(readFloat(self.mockStream, 4), 0.0)
        
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\x3f\x80\x00\x00')
        self.assertEqual(readFloat(self.mockStream, 4), 1.0)
        
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\xc0\x00\x00\x00')
        self.assertEqual(readFloat(self.mockStream, 4), -2.0)
        
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\x3e\xaa\xaa\xab')
        self.assertAlmostEqual(readFloat(self.mockStream, 4), 1.0/3.0)
    
        # 8-bit length
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(readFloat(self.mockStream, 8), 0.0)
        
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\x3f\xf0\x00\x00\x00\x00\x00\x00')
        self.assertEqual(readFloat(self.mockStream, 8), 1.0)
        
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\xc0\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(readFloat(self.mockStream, 8), -2.0)
        
        self.mockStream.seek(0)
        self.mockStream = BytesIO(b'\x3f\xd5\x55\x55\x55\x55\x55\x55')
        self.assertEqual(readFloat(self.mockStream, 8), 1.0/3.0)
    
    
    
    def testReadString(self):
        """ Test reading strings. """
        
        self.mockStream = BytesIO(b'')
        self.assertEqual(readString(self.mockStream, 0), u'')
        
        self.mockStream = BytesIO(b'test')
        mockLen = len(self.mockStream.getvalue())
        self.assertEqual(readString(self.mockStream, mockLen),
                         u'test')
            
    
    
    def testReadUnicode(self):
        """ Test reading unicode strings. """
        
        self.mockStream = BytesIO(b'')
        self.assertEqual(readUnicode(self.mockStream, 0), u'')
        
        self.mockStream = BytesIO(b'TEST')
        mockLen = len(self.mockStream.getvalue())
        self.assertEqual(readUnicode(self.mockStream, mockLen),
                         u'TEST')
    
    
    
    def testReadDate(self):
        """ Test reading dates from bytes. """
        
        self.mockStream = BytesIO(b'\x00\x00\x00\x00ABCD')
        a = readDate(self.mockStream)
        self.assertEqual(a, datetime(2001, 1, 1, tzinfo=None) + \
                            timedelta(microseconds=0x41424344//1000))