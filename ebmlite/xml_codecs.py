"""
Classes for various means of encoding/decoding binary data to/from XML.
"""

import base64
from io import BytesIO, StringIO


class Base64Codec:
    """ Encoder/decoder for binary data as base64 formatted text to/from XML.
    """
    NAME = "base64"

    def __init__(self, cols=78, **kwargs):
        """ Constructor.

            :param cols: The length of each line of base64 data, excluding
                any indentation specified when encoding. If 0 or `None`,
                data will be written as a single continuous block with no
                newlines.

            Additional keyword arguments will be accepted (to maintain
            compatibility with other codecs) but ignored.
         """
        self.cols = cols


    def encode(self, data, stream=None, indent='', **kwargs):
        """ Convert binary data to base64 text.

            :param data: The binary data from an EBML `BinaryElement`.
            :param stream: An optional stream to which to write the encoded
                data.
            :param indent: Indentation before each row of text. Used if
                the codec was instantiated with `cols` specified.
            :returns: If no `stream`, the encoded data as text. If `stream`,
                the number of bytes written.

            Additional keyword arguments will be accepted (to maintain
            compatibility with other codecs) but ignored.
        """
        if isinstance(indent, bytes):
            indent = indent.decode()
        if isinstance(data, str):
            data = data.encode('utf8')

        result = base64.encodebytes(data).decode()
        if stream is None:
            out = StringIO()
        else:
            out = stream

        if self.cols is None:
            if stream is not None:
                return out.write(result)
            return result

        numbytes = 0

        for chunk in range(0, len(result), self.cols):
            numbytes += out.write(indent) + out.write(result[chunk:chunk+self.cols])

        if stream is None:
            return out.getvalue()

        return numbytes


    @classmethod
    def decode(cls, data, stream=None):
        """ Decode binary data in base64 (e.g., from an XML file). Note: this
            is a `classmethod`, and works regardles of how the encoded data was
            formatted (e.g., with indentations and/or line breaks).

            :param data: The base64 data from an XML file.
            :param stream: A stream to which to write the encoded data.
            :returns: If no `stream`, the decoded binary data. If `stream`,
                the number of bytes written.
        """
        if not data:
            if stream is None:
                return b''
            else:
                return 0

        if isinstance(data, str):
            data = data.encode('utf8')

        result = base64.decodebytes(data)

        if stream is not None:
            return stream.write(result)
        else:
            return result


class HexCodec:
    """ Encoder/decoder for binary data as hexadecimal format to/from XML.
        Encoded text is multiple columns of bytes/words (default is 16 columns,
        2 bytes per column), with an optional file offset at the start of each
        row.
    """
    # The name shown in the encoded XML element's `encoding` attribute
    NAME = "hex"

    def __init__(self, width=2, cols=32, offsets=True, **kwargs):
        """ Constructor.

            :param width: The number of bytes displayed per column when
                encoding.
            :param cols: The number of columns to display when encoding. If 0
                or `None`, data will be written as a single continuous block
                with no newlines.
            :param offsets: If `True`, each line will start with its offset
                (in decimal). Applicable if `cols` is a non-zero number.
        """
        self.width = width
        self.cols = cols
        self.offsets = bool(offsets and cols)


    def encode(self, data, stream=None, offset=0, indent='', **kwargs):
        """ Convert binary data to hexadecimal text.

            :param data: The binary data from an EBML `BinaryElement`.
            :param stream: An optional stream to which to write the encoded
                data.
            :param offset: A starting number for the displayed offsets column.
                For showing the data's offset in an EBML file.
            :param indent: Indentation before each row of hex text.
            :returns: If no `stream`, the encoded data as text. If `stream`,
                the number of bytes written.
        """
        if not isinstance(indent, str):
            indent = indent.decode()

        if stream is None:
            out = StringIO()
        else:
            out = stream

        newline = bool(self.cols)
        offsets = self.offsets and newline

        numbytes = 0
        for i, b in enumerate(data):
            if newline and not i % self.cols:
                numbytes += out.write(indent)
                if offsets:
                    numbytes += out.write('\n[{:06d}] '.format(i + offset))
                else:
                    numbytes += out.write('\n')
            elif not i % self.width:
                numbytes += out.write(' ')
            numbytes += out.write('{:02x}'.format(b))

        if stream is None:
            return out.getvalue()

        return numbytes


    @classmethod
    def decode(cls, data, stream=None):
        """ Decode binary data in hexadecimal (e.g., from an XML file). Note:
            this is a `classmethod`, and works regardles of how the encoded
            data was formatted (e.g., number of columns, with or without
            offsets, etc.).

            :param data: The base64 data from an XML file.
            :param stream: A stream to which to write the encoded data.
            :returns: If no `stream`, the decoded binary data. If `stream`,
                the number of bytes written.
        """
        if stream is None:
            out = BytesIO()
        else:
            out = stream
        numbytes = 0

        if not data:
            if stream is None:
                return b''
            else:
                return 0

        if isinstance(data, str):
            data = data.encode('utf8')

        for word in data.split():
            if b'[' in word or b']' in word:
                continue
            for i in range(0, len(word), 2):
                numbytes += out.write((int(word[i:i+2], 16).to_bytes(1, 'big')))

        if stream is None:
            return out.getvalue()

        return numbytes


class IgnoreCodec:
    """ Suppress binary data.
    """
    NAME = "ignore"

    @staticmethod
    def encode(data, stream=None, **kwargs):
        if stream:
            return 0
        return ''

    @staticmethod
    def decode(data, stream=None, **kwargs):
        if stream:
            return 0
        return b''



BINARY_CODECS = {'base64': Base64Codec,
                 'hex': HexCodec,
                 'ignore': IgnoreCodec,
                 }
