"""
Functions for encoding EBML elements and their values.

Note: this module does not encode Document or MasterElement objects; they are
special cases, handled in `core.py`.
"""
__author__ = "David Randall Stokes, Connor Flanigan"
__copyright__ = "Copyright 2021, Mide Technology Corporation"
__credits__ = "David Randall Stokes, Connor Flanigan, Becker Awqatty, Derek Witt"

__all__ = ['encodeBinary', 'encodeDate', 'encodeFloat', 'encodeId', 'encodeInt',
           'encodeSize', 'encodeString', 'encodeUInt', 'encodeUnicode']

import datetime
import struct
import sys
from typing import AnyStr, Optional
import warnings

from .decoding import _struct_uint64, _struct_int64
from .decoding import _struct_float32, _struct_float64

# ==============================================================================
#
# ==============================================================================

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
STRING_CHARACTERS = (b"?"*32 + bytearray(range(32, 127))).ljust(256, b'?')

# ==============================================================================
#
# ==============================================================================


def getLength(val: int) -> int:
    """ Calculate the encoded length of a value.
        :param val: A value to be encoded, generally either an ID or a size for
            an EBML element
        :return The minimum length, in bytes, that can be used to represent val
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
    elif val <= 34359738366:
        return 5
    elif val <= 4398046511102:
        return 6
    elif val <= 562949953421310:
        return 7
    else:
        return 8


def encodeSize(val: Optional[int], length: Optional[int] = None) -> bytes:
    """ Encode an element size.

        :param val: The size to encode. If `None`, the EBML 'unknown' size
            will be returned (1 or `length` bytes, all bits 1).
        :param length: An explicit length for the encoded size. If `None`,
            the size will be encoded at the minimum length required.
        :return: an encoded size for an EBML element.
        :raise ValueError: raised if the length is invalid, or the length cannot
            be encoded.
    """
    if val is None:
        # 'unknown' size: all bits 1.
        length = 1 if (length is None or length == -1) else length
        return b'\xff' * length

    length = getLength(val) if (length is None or length == -1) else length
    try:
        prefix = LENGTH_PREFIXES[length]
        return encodeUInt(val | prefix, length)
    except (IndexError, TypeError, ValueError):
        raise ValueError("Cannot encode element size %s" % length)


# ==============================================================================
# --- Encoding
# ==============================================================================

def encodeId(eid: int, length: Optional[int] = None) -> bytes:
    """ Encode an element ID.

        :param eid: The EBML ID to encode.
        :param length: An explicit length for the encoded data. A `ValueError`
            will be raised if the length is too short to encode the value.
        :return: The binary representation of ID, left-padded with ``0x00`` if
            `length` is not `None`.
        :return: The encoded version of the ID.
        :raise ValueError: raised if length is less than one or more than 4.
    """
    if length is not None:
        if length < 1 or length > 4:
            raise ValueError("Cannot encode an ID 0x%0x to length %d" %
                             (eid, length))
    try:
        return encodeUInt(eid, length)
    except TypeError:
        raise TypeError('Cannot encode {} {!r} as ID'.format(type(eid).__name__, eid))


def encodeUInt(val: int, length: Optional[int] = None) -> bytes:
    """ Encode an unsigned integer.

        :param val: The unsigned integer value to encode.
        :param length: An explicit length for the encoded data. A `ValueError`
            will be raised if the length is too short to encode the value.
        :return: The binary representation of val as an unsigned integer,
            left-padded with ``0x00`` if `length` is not `None`.
        :raise ValueError: raised if val is longer than length.
    """
    if isinstance(val, float):
        fval, val = val, int(val)
        if fval != val:
            warnings.warn('encodeUInt: float value {} encoded as {}'.format(fval, val))
    elif not isinstance(val, int):
        raise TypeError('Cannot encode {} {!r} as unsigned integer'.format(type(val).__name__, val))

    if val < 0:
        raise ValueError('Cannot encode negative value {} as unsigned integer'.format(val))

    pad = b'\x00'

    try:
        packed = _struct_uint64.pack(val).lstrip(pad) or pad
    except struct.error as err:
        # Catch other errors. Value is probably too large for struct.
        raise ValueError(str(err))

    if length is None:
        return packed
    if len(packed) > length:
        raise ValueError("Encoded length (%d) greater than specified length "
                         "(%d)" % (len(packed), length))
    return packed.rjust(length, pad)


def encodeInt(val: int, length: Optional[int] = None) -> bytes:
    """ Encode a signed integer.

        :param val: The signed integer value to encode.
        :param length: An explicit length for the encoded data. A `ValueError`
            will be raised if the length is too short to encode the value.
        :return: The binary representation of val as a signed integer,
            left-padded with either ```0x00`` (for positive values) or ``0xFF``
            (for negative) if `length` is not `None`.
        :raise ValueError: raised if val is longer than length.
    """
    if isinstance(val, float):
        fval, val = val, int(val)
        if fval != val:
            warnings.warn('encodeInt: float value {} encoded as {}'.format(fval, val))

    try:
        if val >= 0:
            pad = b'\x00'
            packed = _struct_int64.pack(val).lstrip(pad) or pad
            if packed[0] & 0b10000000:
                packed = pad + packed
        else:
            pad = b'\xff'
            packed = _struct_int64.pack(val).lstrip(pad) or pad
            if not packed[0] & 0b10000000:
                packed = pad + packed

        if length is None:
            return packed
        if len(packed) > length:
            raise ValueError("Encoded length (%d) greater than specified length "
                             "(%d)" % (len(packed), length))
        return packed.rjust(length, pad)

    except (TypeError, struct.error):
        raise TypeError('Cannot encode {} {!r} as integer'.format(type(val).__name__, val))


def encodeFloat(val: float, length: Optional[int] = None) -> bytes:
    """ Encode a floating point value.

        :param val: The floating point value to encode.
        :param length: An explicit length for the encoded data. Must be
            `None`, 0, 4, or 8; otherwise, a `ValueError` will be raised.
        :return: The binary representation of val as a float, left-padded with
            ``0x00`` if `length` is not `None`.
        :raise ValueError: raised if val not length 0, 4, or 8
    """
    if length is None:
        if val is None or val == 0.0:
            return b''
        else:
            length = DEFAULT_FLOAT_SIZE

    try:
        if length == 0:
            return b''
        if length == 4:
            return _struct_float32.pack(val)
        elif length == 8:
            return _struct_float64.pack(val)
        else:
            raise ValueError("Cannot encode float of length %d; only 0, 4, or 8" %
                             length)
    except struct.error:
        raise TypeError('Cannot encode {} {!r} as float'.format(type(val).__name__, val))


def encodeBinary(val: AnyStr, length: Optional[int] = None) -> bytes:
    """ Encode binary data.

        :param val: A string, bytes, or bytearray containing the data to encode.
        :param length: An explicit length for the encoded data. A
            `ValueError` will be raised if `length` is shorter than the
            actual length of the binary data.
        :return: The binary representation of value as binary data, left-padded
            with ``0x00`` if `length` is not `None`.
        :raise ValueError: raised if val is longer than length.
    """
    if val is None:
        val = b''
    elif isinstance(val, str):
        val = val.encode('utf_8')
    elif not isinstance(val, (bytearray, bytes)):
        raise TypeError('Cannot encode {} {!r} as binary'.format(type(val).__name__, val))

    if length is None:
        return val
    elif len(val) <= length:
        return val.ljust(length, b'\x00')
    else:
        raise ValueError("Length of data (%d) exceeds specified length (%d)" %
                         (len(val), length))


def encodeString(val: AnyStr, length: Optional[int] = None) -> bytes:
    """ Encode an ASCII string.

        :param val: The string (or bytearray) to encode.
        :param length: An explicit length for the encoded data. The result
            will be truncated if the original string is longer.
        :return: The binary representation of val as a string, truncated or
            left-padded with ``0x00`` if `length` is not `None`.
    """
    if isinstance(val, str):
        val = val.encode('ascii', 'replace')
    elif not isinstance(val, (bytearray, bytes)):
        raise TypeError('Cannot encode {} {!r} as ASCII string'.format(type(val).__name__, val))

    if length is not None:
        val = val[:length]

    return encodeBinary(val.translate(STRING_CHARACTERS), length)


def encodeUnicode(val: str, length: Optional[int] = None) -> bytes:
    """ Encode a Unicode string.

        :param val: The Unicode string to encode.
        :param length: An explicit length for the encoded data. The result
            will be truncated if the original string is longer.
        :return: The binary representation of val as a string, truncated or
            left-padded with ``0x00`` if `length` is not `None`.
    """
    if not isinstance(val, (bytearray, bytes, str)):
        raise TypeError('Cannot encode {} {!r} as string'.format(type(val).__name__, val))

    val = val.encode('utf_8')

    if length is not None:
        val = val[:length]

    return encodeBinary(val, length)


def encodeDate(val: datetime.datetime, length: Optional[int] = None) -> bytes:
    """ Encode a `datetime` object as an EBML date (i.e. nanoseconds since
        2001-01-01T00:00:00).

        :param val: The `datetime.datetime` object value to encode.
        :param length: An explicit length for the encoded data. Must be
            `None` or 8; otherwise, a `ValueError` will be raised.
        :return: The binary representation of val as an 8-byte dateTime.
        :raise ValueError: raised if the length of the input is not 8 bytes.
    """
    if length is None:
        length = 8
    elif length != 8:
        raise ValueError("Dates must be of length 8")

    if val is None:
        val = datetime.datetime.utcnow()
    elif not isinstance(val, datetime.datetime):
        raise TypeError('Cannot encode {} {!r} as datetime'.format(type(val).__name__, val))

    delta = val - datetime.datetime(2001, 1, 1, tzinfo=None)
    nanoseconds = (delta.microseconds +
                   ((delta.seconds + (delta.days * 86400)) * 1000000)) * 1000
    return encodeInt(nanoseconds, length)
