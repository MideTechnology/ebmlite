"""
Some utilities for manipulating EBML documents: translate to/from XML, etc.
This module may be imported or used as a command-line utility.

Created on Aug 11, 2017

@todo: Clean up and standardize usage of the term 'size' versus 'length.'
@todo: Modify (or create an alternate version of) `toXml()` that writes
    directly to a file, allowing the conversion of huge EBML files.
@todo: Add other options to command-line utility for the other arguments of
    `toXml()` and `xml2ebml()`.
"""
from io import StringIO

__author__ = "dstokes"
__copyright__ = "Copyright 2017 Mide Technology Corporation"

import ast
from base64 import b64encode, b64decode
import sys
import tempfile
from xml.etree import ElementTree as ET

from . import core, encoding

__all__ = ['toXml', 'xml2ebml', 'loadXml', 'pprint']

# ===============================================================================
#
# ===============================================================================


def toXml(el, parent=None, offsets=True, sizes=True, types=True, ids=True):
    """ Convert an EBML Document to XML. Binary elements will contain
        base64-encoded data in their body. Other non-master elements will
        contain their value in a ``value`` attribute.

        @param el: An instance of an EBML Element or Document subclass.
        @keyword parent: The resulting XML element's parent element, if any.
        @keyword offsets: If `True`, create a ``offset`` attributes for each
            generated XML element, containing the corresponding EBML element's
            offset.
        @keyword sizes: If `True`, create ``size`` attributes containing the
            corresponding EBML element's size.
        @keyword types: If `True`, create ``type`` attributes containing the
            name of the corresponding EBML element type.
        @keyword ids: If `True`, create ``id`` attributes containing the
            corresponding EBML element's EBML ID.
        @return The root XML element of the file.
    """
    if isinstance(el, core.Document):
        elname = el.__class__.__name__
    else:
        elname = el.name

    if parent is None:
        xmlEl = ET.Element(elname)
    else:
        xmlEl = ET.SubElement(parent, elname)
    if isinstance(el, core.Document):
        xmlEl.set('source', el.filename)
        xmlEl.set('schemaName', el.schema.name)
        xmlEl.set('schemaFile', el.schema.filename)
    else:
        if ids and isinstance(el.id, int):
            xmlEl.set('id', "0x%X" % el.id)
        if types:
            xmlEl.set('type', el.dtype.__name__)

    if offsets:
        xmlEl.set('offset', str(el.offset))
    if sizes:
        xmlEl.set('size', str(el.size))

    if isinstance(el, core.MasterElement):
        for chEl in el:
            toXml(chEl, xmlEl, offsets, sizes, types)
    elif isinstance(el, core.BinaryElement):
        xmlEl.text = b64encode(el.value).decode()
    elif not isinstance(el, core.VoidElement):
        xmlEl.set('value', str(el.value).encode('ascii', 'xmlcharrefreplace').decode())

    return xmlEl


#===============================================================================
#
#===============================================================================

def xmlElement2ebml(xmlEl, ebmlFile, schema, sizeLength=None, unknown=True):
    """ Convert an XML element to EBML, recursing if necessary. For converting
        an entire XML document, use `xml2ebml()`.

        @param xmlEl: The XML element. Its tag must match an element defined
            in the `schema`.
        @param ebmlFile: An open file-like stream, to which the EBML data will
            be written.
        @param schema: An `ebmlite.core.Schema` instance to use when
            writing the EBML document.
        @keyword sizeLength:
        @param unknown: If `True`, unknown element names will be allowed,
            provided their XML elements include an ``id`` attribute with the
            EBML ID (in hexadecimal).
        @return The length of the encoded element, including header and children.
        @raise NameError: raised if an xml element is not present in the schema and unknown is False, OR if the xml
            element does not have an ID.
    """
    if not isinstance(xmlEl.tag, (str, bytes, bytearray)):
        # (Probably) a comment; disregard.
        return 0
        
    try:
        cls = schema[xmlEl.tag]
        encId = encoding.encodeId(cls.id)
    except (KeyError, AttributeError):
        # Element name not in schema. Go ahead if allowed (`unknown` is `True`)
        # and the XML element specifies an ID,
        if not unknown:
            raise NameError("Unrecognized EBML element name: %s" % xmlEl.tag)

        eid = xmlEl.get('id', None)
        if eid is None:
            raise NameError("Unrecognized EBML element name with no 'id' "
                            "attribute in XML: %s" % xmlEl.tag)
        cls = core.UnknownElement
        encId = encoding.encodeId(int(eid, 16))
        cls.id = int(eid, 16)

    if sizeLength is None:
        sl = xmlEl.get('sizeLength', None)
        if sl is None:
            s = xmlEl.get('size', None)
            if s is not None:
                sl = encoding.getLength(int(s))
            else:
                sl = 4
        else:
            sl = int(sl)
    else:
        sl = xmlEl.get('sizeLength', sizeLength)

    if issubclass(cls, core.MasterElement):
        ebmlFile.write(encId)
        sizePos = ebmlFile.tell()
        ebmlFile.write(encoding.encodeSize(None, sl))
        size = 0
        for chEl in xmlEl:
            size += xmlElement2ebml(chEl, ebmlFile, schema, sl)
        endPos = ebmlFile.tell()
        ebmlFile.seek(sizePos)
        ebmlFile.write(encoding.encodeSize(size, sl))
        ebmlFile.seek(endPos)
        return len(encId) + (endPos - sizePos)

    elif issubclass(cls, core.BinaryElement):
        if xmlEl.text is None:
            val = b""
        else:
            val = b64decode(xmlEl.text)
    elif issubclass(cls, (core.IntegerElement, core.FloatElement)):
        val = ast.literal_eval(xmlEl.get('value'))
    else:
        val = cls.dtype(xmlEl.get('value'))

    size = xmlEl.get('size', None)
    if size is not None:
        size = int(size)
    sl = xmlEl.get('sizeLength')
    if sl is not None:
        sl = int(sl)

    encoded = cls.encode(val, size, lengthSize=sl)
    ebmlFile.write(encoded)
    return len(encoded)


def xml2ebml(xmlFile, ebmlFile, schema, sizeLength=None, headers=True,
             unknown=True):
    """ Convert an XML file to EBML.

        @todo: Convert XML on the fly, rather than parsing it first, allowing
            for the conversion of arbitrarily huge files.

        @param xmlFile: The XML source. Can be a filename, an open file-like
            stream, or a parsed XML document.
        @param ebmlFile: The EBML file to write. Can be a filename or an open
            file-like stream.
        @param schema: The EBML schema to use. Can be a filename or an
            instance of a `Schema`.
        @keyword sizeLength: The default length of each element's size
            descriptor. Must be large enough to store the largest 'master'
            element. If an XML element has a ``sizeLength`` attribute, it will
            override this.
        @keyword headers: If `True`, generate the standard ``EBML`` EBML
            element if the XML document does not contain one.
        @param unknown: If `True`, unknown element names will be allowed,
            provided their XML elements include an ``id`` attribute with the
            EBML ID (in hexadecimal).
        @return: the size of the ebml file in bytes.
        @raise NameError: raises if an xml element is not present in the schema.
    """
    if isinstance(ebmlFile, (str, bytes, bytearray)):
        ebmlFile = open(ebmlFile, 'wb')
        openedEbml = True
    else:
        openedEbml = False

    if not isinstance(schema, core.Schema):
        schema = core.loadSchema(schema)

    if isinstance(xmlFile, ET.Element):
        # Already a parsed XML element
        xmlRoot = xmlFile
    elif isinstance(xmlFile, ET.ElementTree):
        # Already a parsed XML document
        xmlRoot = xmlFile.getroot()
    else:
        xmlDoc = ET.parse(xmlFile)
        xmlRoot = xmlDoc.getroot()

    if xmlRoot.tag not in schema and xmlRoot.tag != schema.document.__name__:
        raise NameError("XML element %s not an element or document in "
                        "schema %s (wrong schema)" % (xmlRoot.tag, schema.name))

    headers = headers and 'EBML' in schema
    if headers and 'EBML' not in (el.tag for el in xmlRoot):
        pos = ebmlFile.tell()
        cls = schema.document
        ebmlFile.write(cls.encodePayload(cls._createHeaders()))
        numBytes = ebmlFile.tell() - pos
    else:
        numBytes = 0

    if xmlRoot.tag == schema.document.__name__:
        for el in xmlRoot:
            numBytes += xmlElement2ebml(el, ebmlFile, schema, sizeLength,
                                        unknown=unknown)
    else:
        numBytes += xmlElement2ebml(xmlRoot, ebmlFile, schema, sizeLength,
                                    unknown=unknown)

    if openedEbml:
        ebmlFile.close()

    return numBytes

#===============================================================================
#
#===============================================================================

def loadXml(xmlFile, schema, ebmlFile=None):
    """ Helpful utility to load an EBML document from an XML file.

        @param xmlFile: The XML source. Can be a filename, an open file-like
            stream, or a parsed XML document.
        @param schema: The EBML schema to use. Can be a filename or an
            instance of a `Schema`.
        @keyword ebmlFile: The name of the temporary EBML file to write, or
            ``:memory:`` to use RAM (like `sqlite3`). Defaults to an
            automatically-generated temporary file.
        @return The root node of the specified EBML file.
    """
    if ebmlFile == ":memory:":
        ebmlFile = StringIO()
        xml2ebml(xmlFile, ebmlFile, schema)
        ebmlFile.seek(0)
    else:
        ebmlFile = tempfile.mktemp() if ebmlFile is None else ebmlFile
        xml2ebml(xmlFile, ebmlFile, schema)

    return schema.load(ebmlFile)


#===============================================================================
#
#===============================================================================

def pprint(el, values=True, out=sys.stdout, indent="  ", _depth=0):
    """ Test function to recursively crawl an EBML document or element and
        print its structure, with child elements shown indented.

        @param el: An instance of a `Document` or `Element` subclass.
        @keyword values: If `True`, show elements' values.
        @keyword out: A file-like stream to which to write.
        @keyword indent: The string containing the character(s) used for each
            indentation.
    """
    tab = indent * _depth

    if _depth == 0:
        if values:
            out.write("Offset Size   Element (ID): Value\n")
        else:
            out.write("Offset Size   Element (ID)\n")
        out.write("====== ====== =================================\n")

    if isinstance(el, core.Document):
        out.write("%06s %06s %s %s (Document, type %s)\n" % (el.offset, el.size, tab, el.name, el.type))
        for i in el:
            pprint(i, values, out, indent, _depth+1)
    else:
        out.write("%06s %06s %s %s (ID 0x%0X)" % (el.offset, el.size, tab, el.name, el.id))
        if isinstance(el, core.MasterElement):
            out.write(": (master) %d subelements\n" % len(el.value))
            for i in el:
                pprint(i, values, out, indent, _depth+1)
        else:
            out.write(": (%s)" % el.dtype.__name__)
            if values and not isinstance(el, core.BinaryElement):
                out.write(" %r\n" % (el.value))
            else:
                out.write("\n")

    out.flush()


#===============================================================================
#
#===============================================================================

if __name__ == "__main__":
    import argparse
    import os.path
    from xml.dom.minidom import parseString

    def errPrint(msg):
        sys.stderr.write("%s\n" % msg)
        sys.stderr.flush()
        exit(1)


    argparser = argparse.ArgumentParser(description="""
        ebmlite utilities: some basic command-line tools for converting between
        XML and EBML and viewing the structure of an EBML file.
        """)

    argparser.add_argument('mode',
                           choices=["xml2ebml", "ebml2xml", "view"],
                           help="The utility to run.")
    argparser.add_argument('input',
                           metavar="[FILE.ebml|FILE.xml]",
                           help="""The source file: XML for 'xml2ebml,' EBML
                                   for 'ebml2xml' or 'view.'""")
    argparser.add_argument('schema',
                           metavar="SCHEMA.xml",
                           help="""The name of the schema file. Only the name
                                   itself is required if the schema file is in
                                   the standard schema directory.""")
    argparser.add_argument('-o', '--output',
                           metavar="[FILE.xml|FILE.ebml]",
                           help="The output file.")
    argparser.add_argument('-c', '--clobber',
                           action="store_true",
                           help="Clobber (overwrite) existing files.")
    argparser.add_argument('-p', '--pretty',
                           action="store_true",
                           help="Generate 'pretty' XML with ebml2xml.")

    args = argparser.parse_args()

    if not os.path.exists(args.input):
        sys.stderr.write("Input file does not exist: %s\n" % args.input)
        exit(1)

    try:
        schema = core.loadSchema(args.schema)
    except IOError as err:
        errPrint("Error loading schema: %s\n" % err)

    if args.output:
        output = os.path.realpath(os.path.expanduser(args.output))
        if os.path.exists(output) and not args.clobber:
            errPrint("Output file exists: %s" % args.output)
        out = open(output, 'wb')
    else:
        out = sys.stdout

    if args.mode == "xml2ebml":
        xml2ebml(args.input, out, schema)  # , sizeLength=4, headers=True, unknown=True)
    elif args.mode == "ebml2xml":
        doc = schema.load(args.input, headers=True)
        root = toXml(doc)  # , offsets, sizes, types, ids)
        s = ET.tostring(root, encoding="utf-8")
        if args.pretty:
            parseString(s).writexml(out, addindent=b'\t', newl=b'\n', encoding=b'utf-8')
        else:
            out.write(s)
    else:
        doc = schema.load(args.input, headers=True)
        pprint(doc, out=out)

    if out != sys.stdout:
        out.close()

    exit(0)
