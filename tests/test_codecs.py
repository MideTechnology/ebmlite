import collections
import datetime
import types
import random
import unittest
from io import BytesIO

from ebmlite import xml_codecs

class testCodecs(unittest.TestCase):
    """ Tests for the binary codecs for converting to/from test (e.g. XML).
    """
    def setUp(self):
        self.codecs = {n: c for n, c in xml_codecs.BINARY_CODECS.items()
                       if n != 'ignore'}

        random.seed(42)
        self.testData = bytes(random.randint(0, 255) for _ in range(1024))


    def test_codec_basics(self):
        """ Test basic encoding/decoding functionality. """
        for Codec in self.codecs.values():
            codec = Codec()
            garbageIn = codec.encode(self.testData)
            garbageOut = codec.decode(garbageIn)
            self.assertEqual(garbageOut, self.testData)


    def test_ignore_codec(self):
        """ Test the `IgnoreCodec`, which outputs nothing. """
        ignore = xml_codecs.BINARY_CODECS['ignore']()
        self.assertEqual(len(ignore.encode(self.testData)), 0,
             "IgnoreCodec.encode() returned content, should have returned ''")
        self.assertEqual(len(ignore.decode("ignore me")), 0,
             "IgnoreCodec.decode() returned content, should have returned b''")
