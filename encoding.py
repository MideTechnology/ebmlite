'''
Module mide_ebml.ebmlite.encoding

Created on Aug 11, 2017
'''

__author__ = "dstokes"
__copyright__ = "Copyright 2017 Mide Technology Corporation"

import datetime
import sys

from decoding import _struct_uint64, _struct_int64
from decoding import _struct_float32, _struct_float64

#===============================================================================
# 
#===============================================================================

# If no length is given, use the platform's size of a float.
DEFAULT_FLOAT_SIZE = 4 if sys.maxsize <= 2147483647 else 8

LENGTH_PREFIXES = [0,
                   0x80,
                   0x4000,
                   0x200000,
                   0x10000000,
                   0x0800000000,
                   0x040000000000,
                   0x02000000000000,
                   0x0100000000000000
                   ]

# Translation table for removing invalid EBML string characters (32 < x < 127)
STRING_CHARACTERS = (b"?"*32 + bytearray(range(32,127))).ljust(256, b'?')

#===============================================================================
# 
#===============================================================================

def getLength(val):
    """ Calculate the encoded length of a value.
    """
    # Brute force it. Ugly but faster than calculating it.
    if val <= 126:
        return 1
    elif val <= 16382:
        return 2
    elif val <= 2097150:
        return 3
    elif val <= 268435454:
        return 4
    elif val <= 34359738366L:
        return 5
    elif val <= 4398046511102L:
        return 6
    elif val <= 562949953421310L:
        return 7
    else:
        return 8


def encodeSize(val, length=None):
    """ Encode an element size.
    
        @param val: The size to encode. If `None`, the EBML 'unknown' size
            will be returned (1 or `length` bytes, all bits 1).
        @keyword length: An explicit length for the encoded size. If `None`,
            the size will be encoded at the minimum length required.
    """
    if val is None:
        # 'unknown' size: all bits 1.
        length = 1 if length is None else length
        return b'\xff' * length
    
    length = getLength(val) if length is None else length
    try:
        prefix = LENGTH_PREFIXES[length]
        return encodeUInt(val|prefix, length)
    except (IndexError, TypeError):
        raise ValueError("Cannot encode element size %s" % length)


#===============================================================================
#--- Encoding
#===============================================================================

def encodeId(eid, length=None):
    """ Encode an element ID.

        @param eid: The EBML ID to encode.
        @keyword length: An explicit length for the encoded data. A `ValueError`
            will be raised if the length is too short to encode the value.
    """
    if length is not None:
        if length < 1 or length > 4:
            raise ValueError("Cannot encode an ID 0x%0x to length %d" % 
                             (eid, length))
    return encodeUInt(eid, length)


def encodeUInt(val, length=None):
    """ Encode an unsigned integer.

        @param val: The unsigned integer value to encode.
        @keyword length: An explicit length for the encoded data. A `ValueError`
            will be raised if the length is too short to encode the value.
    """
    packed = _struct_uint64.pack(val).lstrip(b'\x00')
    if length is None:
        return packed
    if len(packed) > length:
        raise ValueError("Encoded length (%d) greater than specified length "
                         "(%d)" % (len(packed), length))
    return packed.rjust(length, b'\x00')


def encodeInt(val, length=None):
    """ Encode a signed integer.

        @param val: The signed integer value to encode.
        @keyword length: An explicit length for the encoded data. A `ValueError`
            will be raised if the length is too short to encode the value.
    """
    pad = b"\xff" if val < 0 else b"\x00"
    packed = _struct_int64.pack(val).lstrip(pad)
    if length is None:
        return packed
    if len(packed) > length:
        raise ValueError("Encoded length (%d) greater than specified length "
                         "(%d)" % (len(packed), length))
    return packed.rjust(length, pad)


def encodeFloat(val, length=None):
    """ Encode a floating point value.

        @param val: The floating point value to encode.
        @keyword length: An explicit length for the encoded data. Must be
            `None`, 0, 4, or 8; otherwise, a `ValueError` will be raised.
    """
    if length is None:
        if val is None or val == 0.0:
            return ''
        else:
            length = DEFAULT_FLOAT_SIZE

    if length == 0:
        return ''
    if length == 4:
        return _struct_float32.pack(val)
    elif length == 8:
        return _struct_float64.pack(val)
    else:
        raise ValueError("Cannot encode float of length %d; only 0, 4, or 8" % 
                         length)


def encodeBinary(val, length=None):
    """ Encode binary data.
        
        @param val: A string or bytearray containing the data to encode.
        @keyword length: An explicit length for the encoded data. A 
            `ValueError` will be raised if `length` is shorter than the
            actual length of the binary data.
    """
    if isinstance(val, unicode):
        val = val.encode('utf_8')
    elif val is None:
        val = ''

    if length is None:
        return val
    elif len(val) <= length:
        return val.ljust(length, b'\x00')
    else:
        raise ValueError("Length of data (%d) exceeds specified length (%d)" %
                         (len(val), length))
    

def encodeString(val, length=None):
    """ Encode an ASCII string.

        @param val: The string (or bytearray) to encode.
        @keyword length: An explicit length for the encoded data. The result
            will be truncated if the length is less than that of the original.
    """
    if isinstance(val, unicode):
        val = val.encode('ascii', 'replace')
        
    if length is not None:
        val = val[:length]

    return encodeBinary(val.translate(STRING_CHARACTERS), length)


def encodeUnicode(val, length=None):
    """ Encode a Unicode string.

        @param val: The Unicode string to encode.
        @keyword length: An explicit length for the encoded data. The result
            will be truncated if the length is less than that of the original.
    """
    val = val.encode('utf_8')
    
    if length is not None:
        val = val[:length]

    return encodeBinary(val, length)


def encodeDate(val, length=None):
    """ Encode a `datetime` object as an EBML date (i.e. nanoseconds since
        2001-01-01T00:00:00).

        @param val: The `datetime.datetime` object value to encode.
        @keyword length: An explicit length for the encoded data. Must be
            `None` or 8; otherwise, a `ValueError` will be raised.
    """
    if length is None:
        length = 8
    elif length != 8:
        raise ValueError("Dates must be of length 8")

    if val is None:
        val = datetime.datetime.utcnow()

    delta = val - datetime.datetime(2001, 1, 1, tzinfo=None)
    nanoseconds = (delta.microseconds +
                   ((delta.seconds + (delta.days * 86400)) * 1000000)) * 1000
    return encodeInt(nanoseconds, length)
