'''
EBMLite: A lightweight EBML parsing library. It is designed to crawl through
EBML files quickly and efficiently, and that's about it.

Created on Apr 27, 2017

@todo: Unit tests.
@todo: Complete EBML encoding. Specifically, make 'master' elements write 
    directly to the stream, rather than build bytearrays, so huge 'master' 
    elements can be handled.
@todo: Validation. Enforce hierarchy defined in new schema format.
@todo: Proper support for 'infinite' master elements (i.e `size` is `None`).
    Requires validation.
@todo: Document-wide caching, for future handling of streamed data.
@todo: Clean up and standardize usage of the term 'size' versus 'length.'
@todo: (longer term) Consider making schema loading automatic based on the EBML
    DocType, DocTypeVersion, and DocTypeReadVersion. Would mean a refactoring
    of how schemata are loaded.
@todo: (longer term) Refactor to support streaming data. This will require
    modifying the indexing and iterating methods of `Document`.
'''

__author__ = "dstokes"
__copyright__ = "Copyright 2018 Mide Technology Corporation"

__all__ = ['BinaryElement', 'DateElement', 'Document', 'Element', 
           'FloatElement', 'IntegerElement', 'MasterElement', 'Schema', 
           'StringElement', 'UIntegerElement','UnicodeElement', 
           'UnknownElement', 'VoidElement', 'loadSchema']

from ast import literal_eval
from collections import OrderedDict
from datetime import datetime
import errno
import os.path
from StringIO import StringIO
from xml.etree import ElementTree as ET

from decoding import readElementID, readElementSize
from decoding import readFloat, readInt, readUInt, readDate
from decoding import readString, readUnicode
import encoding
import schemata

#===============================================================================
#
#===============================================================================

# SCHEMA_PATH: A list of paths for schema XML files, similar to `sys.path`.
# When `loadSchema()` is used, it will search these paths, in order, to find
# the schema file.
SCHEMA_PATH = ['', 
               os.path.realpath(os.path.dirname(schemata.__file__))]

# SCHEMATA: A dictionary of loaded schemata, keyed by filename. Used by
# `loadSchema()`. In most cases, SCHEMATA should not be otherwise modified.
SCHEMATA = {}


#===============================================================================
#
#===============================================================================

class Element(object):
    """ Base class for all EBML elements. 
        
        @cvar id: The element's EBML ID.
        @cvar name: The element's name. 
        @cvar schema: The `Schema` to which this element belongs.
        @cvar multiple: Can this element be appear multiple times? Note: 
            Currently only enforced for encoding.
        @cvar mandatory: Must this element appear in all EBML files using
            this element's schema? Note: Not currently enforced.
        @cvar children: A list of valid child element types. Only applicable to
            `Document` and `Master` subclasses. Note: Not currently enforced.
        @cvar dtype: The element's native Python data type.
        @cvar precache: If `True`, the Element's value is read when the Element
            is parsed. if `False`, the value is lazy-loaded when needed.
            Numeric element types default to `True`.
        @cvar length: An explicit length (in bytes) of the element when
            encoding. `None` will use standard EBML variable-length encoding.
    """
    # Python native data type.
    dtype = bytearray

    # Should this element's value be read/cached when the element is parsed?
    precache = False

    # Do valid EBML documents require this element?
    mandatory = False
    
    # Does a valid EBML document permit more than one of the element?
    multiple = False

    # Explicit length for this Element subclass, used for encoding.
    length = None
    
    # For python-ebml compatibility; not currently used.
    children = None
    
    
    def parse(self, stream, size):
        """ Type-specific helper function for parsing the element's payload.
            It is assumed the file pointer is at the start of the payload.
        """
        # Document-wide caching could be implemented here.
        return  bytearray(stream.read(size))


    def __init__(self, stream=None, offset=0, size=0, payloadOffset=0):
        """ Constructor. Instantiate a new Element from a file. In most cases,
            elements should be created when a `Document` is loaded, rather
            than instantiated explicitly.
        
            @keyword stream: A file-like object containing EBML data.
            @keyword offset: The element's starting location in the file.
            @keyword size: The size of the whole element.
            @keyword payloadOffset: The starting location of the element's
                payload (i.e. immediately after the element's header).
        """
        self.stream = stream
        self.offset = offset
        self.size = size
        self.payloadOffset = payloadOffset
        self._value = None

        # For python-ebml compatibility. Remove later.
        self.bodySize = size + (payloadOffset - offset)


    def __repr__(self):
        return "<%s (ID:0x%02X), offset %s, size %s>" % \
            (self.__class__.__name__, self.id, self.offset, self.size)


    def __eq__(self, other):
        """ Equality check. Elements are considered equal if they are the same
            type and have the same ID, size, offset, and schema. Note: element
            value is not considered! Check for value equality explicitly 
            (e.g. ``el1.value == el2.value``).
        """
        if other is self:
            return True
        try:
            return (self.dtype == other.dtype
                    and self.id == other.id 
                    and self.offset == other.offset
                    and self.size == other.size 
                    and self.schema == other.schema)
        except AttributeError:
            return False


    @property
    def value(self):
        """ Parse and cache the element's value. """
        if self._value is not None:
            return self._value
        self.stream.seek(self.payloadOffset)
        self._value = self.parse(self.stream, self.size)
        return self._value


    def getRaw(self):
        """ Get the element's raw binary data, including EBML headers.
        """
        self.stream.seek(self.offset)
        return self.stream.read(self.size + (self.payloadOffset - self.offset))
        
    
    def getRawValue(self):
        """ Get the raw binary of the element's value.
        """
        self.stream.seek(self.payloadOffset)
        return self.stream.read(self.size)


    #===========================================================================
    # Caching (experimental)
    #===========================================================================

    def gc(self, recurse=False):
        """ Clear any cached values. To save memory and/or force values to be
            re-read from the file. Returns the number of cached values cleared.
        """
        if self._value is None:
            return 0
        
        self._value = None
        return 1


    #===========================================================================
    # Encoding 
    #===========================================================================
    
    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder. """
        return encoding.encodeBinary(data, length)
         
     
    @classmethod
    def encode(cls, value, length=None, lengthSize=None):
        """ Encode an EBML element.
            
            @param value: The value to encode, or a list of values to encode.
                If a list is provided, each item will be encoded as its own
                element.
            @keyword length: An explicit length for the encoded data, 
                overriding the variable length encoding. For producing
                byte-aligned structures.
            @keyword lengthSize: An explicit length for the encoded element
                size, overriding the variable length encoding.
            @return: A bytearray containing the encoded EBML data.
        """ 
        length = cls.length if length is None else length
        if isinstance(value, (list, tuple)):
            if not cls.multiple:
                raise ValueError("Multiple %s elements per parent not permitted" 
                                 % cls.name)
            result = bytearray()
            for v in value:
                result.extend(cls.encode(v, length=length, lengthSize=lengthSize))
            return result
        payload = cls.encodePayload(value, length=length)
        length = length or len(payload)
        encId = encoding.encodeId(cls.id) 
        return encId + encoding.encodeSize(length, lengthSize) + payload
        

    def dump(self):
        """ Dump this element's value as nested dictionaries, keyed by
            element name. For non-master elements, this just returns the
            element's value; this method exists to maintain uniformity. 
        """
        return self.value


#===============================================================================

class IntegerElement(Element):
    """ Base class for an EBML signed integer element. Schema-specific
        subclasses are generated when a `Schema` is loaded.
    """
    dtype = int
    precache = True

    def parse(self, stream, size):
        """ Type-specific helper function for parsing the element's payload.
            It is assumed the file pointer is at the start of the payload.
        """
        return readInt(stream, size)


    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder for signed integer elements. """
        return encoding.encodeInt(data, length)


#===============================================================================

class UIntegerElement(IntegerElement):
    """ Base class for an EBML unsigned integer element. Schema-specific
        subclasses are generated when a `Schema` is loaded.
    """
    dtype = int
    precache = True

    def parse(self, stream, size):
        """ Type-specific helper function for parsing the element's payload.
            It is assumed the file pointer is at the start of the payload.
        """
        return readUInt(stream, size)


    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder for unsigned integer elements. """
        return encoding.encodeUInt(data, length)


#===============================================================================

class FloatElement(Element):
    """ Base class for an EBML floating point element. Schema-specific
        subclasses are generated when a `Schema` is loaded.
    """
    dtype = float
    precache = True

    def parse(self, stream, size):
        """ Type-specific helper function for parsing the element's payload. 
            It is assumed the file pointer is at the start of the payload.
        """
        return readFloat(stream, size)


    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder for floating point elements. """
        return encoding.encodeFloat(data, length)


#===============================================================================

class StringElement(Element):
    """ Base class for an EBML ASCII string element. Schema-specific
        subclasses are generated when a `Schema` is loaded.
    """
    dtype = str

    def parse(self, stream, size):
        """ Type-specific helper function for parsing the element's payload. 
            It is assumed the file pointer is at the start of the payload.
        """
        return readString(stream, size)


    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder for ASCII string elements. """
        return encoding.encodeString(data, length)



#===============================================================================

class UnicodeElement(StringElement):
    """ Base class for an EBML UTF-8 string element. Schema-specific subclasses
        are generated when a `Schema` is loaded.
    """
    dtype = unicode

    def parse(self, stream, size):
        """ Type-specific helper function for parsing the element's payload. 
            It is assumed the file pointer is at the start of the payload.
        """
        return readUnicode(stream, size)


    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder for Unicode string elements. """
        return encoding.encodeUnicode(data, length)


#===============================================================================

class DateElement(IntegerElement):
    """ Base class for an EBML 'date' element. Schema-specific subclasses are
        generated when a `Schema` is loaded.
    """
    dtype = datetime

    def parse(self, stream, size):
        """ Type-specific helper function for parsing the element's payload. 
            It is assumed the file pointer is at the start of the payload.
        """
        return readDate(stream, size)


    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder for date elements. """
        return encoding.encodeDate(data, length)



#===============================================================================

class BinaryElement(Element):
    """ Base class for an EBML 'binary' element. Schema-specific subclasses are
        generated when a `Schema` is loaded.
    """


#===============================================================================

class VoidElement(BinaryElement):
    """ Special case ``Void`` element. Its contents are ignored; they are never
        even read. 
    """
   
    def parse(self, stream, size):
        return bytearray()


    @classmethod
    def encodePayload(cls, data, length=0):
        """ Type-specific payload encoder for Void elements. """
        length = 0 if length is None else length
        return bytearray('\xff' * length)


#===============================================================================

class UnknownElement(BinaryElement):
    """ Special case ``Unknown`` element, used for elements with IDs not present
        in a schema. Unlike other elements, each instance has its own ID. 
    """
    name = "UnknownElement"
    precache = False

    def __eq__(self, other):
        """ Equality check. Unknown elements are considered equal if they have
            the same ID and value. Note that this differs from the criteria
            used for other element classes! 
        """
        if other is self:
            return True
        try:
            return (self.name == other.name
                    and self.id == other.id
                    and self.value == other.value)
        except AttributeError:
            return False


#===============================================================================

class MasterElement(Element):
    """ Base class for an EBML 'master' element, a container for other
        elements.
    """
    dtype = list

    def parse(self):
        """ Type-specific helper function for parsing the element's payload. """
        # Special case; unlike other elements, value() property doesn't call 
        # parse(). Used only when pre-caching. 
        return self.value


    def parseElement(self, stream):
        """ Read the next element from a stream, instantiate a `MasterElement` 
            object, and then return it and the offset of the next element
            (this element's position + size).
        """
        offset = stream.tell()
        eid, idlen = readElementID(stream)
        esize, sizelen = readElementSize(stream)
        payloadOffset = offset + idlen + sizelen

        try:
            # TODO: Enforce structure dictated by the schema by using only the
            # elements that are children of this one, or are 'global.' Also,
            # handle 'unknown' size elements, which end with the first invalid
            # child element.
            etype = self.schema.elements[eid]
            el = etype(stream, offset, esize, payloadOffset)
        except KeyError:
            el = UnknownElement(stream, offset, esize, payloadOffset)
            el.id = eid
            el.schema = getattr(self, "schema", None)
        
        if el.precache:
            # Read the value now, avoiding a seek later.
            el._value = el.parse(stream, esize)

        return el, payloadOffset + esize


    def __iter__(self):
        # TODO: Support elements with 'unknown' length (quit when an invalid
        # child element is read).
        pos = self.payloadOffset
        payloadEnd = pos + self.size
        while pos < payloadEnd:
            self.stream.seek(pos)
            el, pos = self.parseElement(self.stream)
            yield el


    def __len__(self):
        """ x.__len__() <==> len(x)
        """
        if self._value is not None:
            return len(self._value)
        try:
            return self._length
        except AttributeError:
            for n, _el in enumerate(self):
                self._length = n
        return self._length

    
    @property
    def value(self):
        """ Parse and cache the element's value. 
        """
        if self._value is not None:
            return self._value
        self._value = list(self)
        return self._value


    def __getitem__(self, *args):
        return self.value.__getitem__(*args)


    #===========================================================================
    # Caching (experimental!)
    #===========================================================================
    
    def gc(self, recurse=False):
        """ Clear any cached values. To save memory and/or force values to be
            re-read from the file.
        """
        cleared = 0
        if self._value is not None:
            if recurse:
                cleared = sum(ch.gc(recurse) for ch in self._value) + 1
            self._value = None
        return cleared
            

    #===========================================================================
    # Encoding
    #===========================================================================
    
    @classmethod
    def encodePayload(cls, data, length=None):
        """ Type-specific payload encoder for 'master' elements. 
        """
        if isinstance(data, dict):
            data = data.items()
        elif not isinstance(data, (list, tuple)):
            raise TypeError("wrong type for %s payload: %s" % (cls.name, 
                                                               type(data)))
        result = bytearray()
        for k,v in data:
            if k not in cls.schema:
                raise TypeError("Element type %r not found in schema" % k)
            # TODO: Validation of hierarchy, multiplicity, mandate, etc.
            result.extend(cls.schema[k].encode(v))
         
        return result

    
    @classmethod
    def encode(cls, data, **kwargs):
        """ Encode an EBML master element.
            
            @param data: The data to encode, provided as a dictionary keyed by
                element name, a list of two-item name/value tuples, or a list
                of either. Note: individual items in a list of name/value pairs
                *must* be tuples!
            @return: A bytearray containing the encoded EBML binary.
        """ 
        if isinstance(data, list) and len(data)>0 and isinstance(data[0],list):
            # List of lists: special case for 'master' elements.
            # Encode as multiple 'master' elements.
            result = bytearray()
            for v in data:
                result.extend(cls.encode(v))
            return result
        return super(MasterElement, cls).encode(data)


    def dump(self):
        """ Dump this element's value as nested dictionaries, keyed by
            element name. The values of 'multiple' elements return as lists.
            Note: The order of 'multiple' elements relative to other elements
            will be lost; a file containing elements ``A1 B1 A2 B2 A3 B3`` will
            result in``[A1 A2 A3][B1 B2 B3]``.
            
            @todo: Decide if this should be in the `util` submodule. It is
                very specific, and it isn't totally necessary for the core 
                library.
        """
        result = OrderedDict()
        for el in self:
            if el.multiple:
                result.setdefault(el.name, []).append(el.dump())
            else:
                result[el.name] = el.dump()
        return result


#===============================================================================
# 
#===============================================================================

class Document(MasterElement):
    """ Base class for an EBML document, containing multiple 'root' elements.
        Loading a `Schema` generates a subclass.
    """

    def __init__(self, stream, name=None, size=None, headers=False):
        """ Constructor. Instantiate a `Document` from a file-like stream.
            In most cases, `Schema.load()` should be used instead of 
            explicitly instantiating a `Document`.
        
            @param stream: A stream object (e.g. a file) from which to read 
                the EBML content, or a filename. 
            @keyword name: The name of the document. Defaults to the filename
                (if applicable).
            @keyword size: The size of the document, in bytes. Use if the
                stream is neither a file or a `StringIO` object.
            @keyword headers: If `False`, the file's ``EBML`` header element 
                (if present) will not appear as a root element in the document.
                The contents of the ``EBML`` element will always be read,
                regardless, and stored in the Document's `info` attribute.
        """
        if not all((hasattr(stream, 'read'), 
                    hasattr(stream, 'tell'),
                    hasattr(stream, 'seek'))):
            raise TypeError('Object %r does not have the necessary stream methods' % stream)
        
        self._value = None
        self.stream = stream
        self.size = size
        self.name = name
        self.id = None # Not applicable to Documents.
        self.offset = self.payloadOffset = self.stream.tell()

        try:
            self.filename = stream.name
        except AttributeError:
            self.filename = ""
            
        if name is None:
            if self.filename:
                self.name = os.path.splitext(os.path.basename(self.filename))[0]
            else:
                self.name = self.__class__.__name__

        if size is None:
            # Note: this doesn't work for cStringIO!
            if isinstance(stream, StringIO):
                self.size = stream.len
            elif self.filename and os.path.exists(self.filename):
                self.size = os.path.getsize(self.stream.name)

        self.info = {}
        
        try:
            # Attempt to read the first element, which should be an EBML header.
            el, pos = self.parseElement(self.stream)
            if el.name == "EBML":
                # Load 'header' info from the file
                self.info = el.dump()
                if not headers:
                    self.payloadOffset = pos
        except:
            # Failed to read the first element. Don't raise here; do that when
            # the Document is actually used.
            pass
        
        if self.size is not None:
            self.bodySize = self.size - self.payloadOffset
        else:
            self.bodySize = None


    def __repr__(self):
        """ "x.__repr__() <==> repr(x) """
        if self.name == self.__class__.__name__:
            return object.__repr__(self)
        return "<%s %r at 0x%08X>" % (self.__class__.__name__, self.name, 
                                      id(self))


    def close(self):
        """ Close the EBML file. Should generally be used only if the object was
            created using a filename, rather than a stream.
        """
        self.stream.close()


    def __len__(self):
        """ x.__len__() <==> len(x)
            Not recommended for huge documents. 
        """
        try:
            return self._length
        except AttributeError:
            for n, _el in enumerate(self):
                self._length = n
        return self._length


    def __iter__(self):
        """ Iterate root elements.
        """
        # TODO: Cache root elements, prevent unnecessary duplicates. Maybe a 
        # dict keyed by offset?
        pos = self.payloadOffset
        while True:
            self.stream.seek(pos)
            try:
                el, pos = self.parseElement(self.stream)
                yield el
            except TypeError as err:
                # Occurs at end of file (parsing 0 length string), it's okay.
                if "ord()" not in str(err):
                    # (Apparently) not the TypeError raised at EOF!
                    raise
                break


    @property
    def roots(self):
        """ The document's root elements. For python-ebml compatibility.
            Using this with large files is not recommended; consider iterating
            instead.
        """
        return list(self)


    @property
    def value(self):
        """ An iterator for iterating the document's root elements. Same as
            `Document.__iter__()`.
        """
        # 'value' not really applicable to a document; return an iterator.
        return iter(self)


    def __getitem__(self, idx):
        """ Get one of the document's root elements by index. 
        """
        # TODO: Cache parsed root elements, handle indexing dynamically.
        if isinstance(idx, (int, long)):
            if idx < 0:
                raise IndexError("Negative indices in a Document not (yet) supported")
            for n, el in enumerate(self):
                if n == idx:
                    return el
            raise IndexError("list index out of range (0-%d)" % (n-1))
        elif isinstance(idx, slice):
            raise IndexError("Document root slicing not (yet) supported")
        else:
            raise TypeError("list indices must be integers, not %s" % type(idx))


    @property
    def version(self):
        """ The document's type version (i.e. the EBML ``DocTypeVersion``). """
        return self.info.get('DocTypeVersion')


    @property
    def type(self):
        """ The document's type name (i.e. the EBML ``DocType``). """
        return self.info.get('DocType')
        

    #===========================================================================
    # Caching (experimental!)
    #===========================================================================
    
    def gc(self, recurse=False):
        # TODO: Implement this if/when caching of root elements is implemented.
        return 0


    #===========================================================================
    # Encoding
    #===========================================================================

    @classmethod
    def _createHeaders(cls):
        """ Create the default EBML 'header' elements for a Document, using
            the default values in the schema.
            
            @return: A dictionary containing a single key (``EBML``) with a
                dictionary as its value. The child dictionary contains
                element names and values.
        """
        if 'EBML' not in cls.schema:
            return {}
        
        headers = OrderedDict()
        for elName, elType in (('EBMLVersion', int), 
                               ('EBMLReadVersion', int),
                               ('DocType', str),
                               ('DocTypeVersion', int),
                               ('DocTypeReadVersion', int)):
            if elName in cls.schema:
                v = cls.schema._getInfo(cls.schema[elName].id, elType)
                if v is not None:
                    headers[elName] = v
                    
        return OrderedDict(EBML=headers)
    
        
    @classmethod
    def encode(cls, stream, data, headers=False, **kwargs):
        """ Encode an EBML document.
            
            @param value: The data to encode, provided as a dictionary keyed by
                element name, or a list of two-item name/value tuples. Note: 
                individual items in a list of name/value pairs *must* be tuples!
            @return: A bytearray containing the encoded EBML binary.
        """ 
        if headers is True:
            stream.write(cls.encodePayload(cls._createHeaders()))
            
        if isinstance(data, list):
            if len(data)>0 and isinstance(data[0],list):
                # List of lists: special case for Documents.
                # Encode as multiple 'root' elements.
                raise TypeError('Cannot encode multiple Documents')
            else:
                for v in data:
                    stream.write(cls.encodePayload(v))
        else:
            stream.write(cls.encodePayload(data))


#===============================================================================
#
#===============================================================================

class Schema(object):
    """ An EBML schema, mapping element IDs to names and data types. Unlike the
        document and element types, this is not a base class; all schemata are
        actual instances of this class.
    
        @ivar document: The schema's Document subclass.
        @ivar elements: A dictionary mapping element IDs to the schema's
            corresponding `Element` subclasses.
        @ivar elementsByName: A dictionary mapping element names to the schema's
            corresponding `Element` subclasses.
        @ivar elementInfo: A dictionary mapping IDs to the raw schema attribute
            data. Is likely to have additional items not present in the created
            element class' attributes.
        
        @ivar source: The source from which the Schema was loaded; either a
            filename or a file-like stream.
        @ivar filename: The absolute path of the source file, if the source
            was a file or a filename.
    """

    BASE_CLASSES = {
        'BinaryElement': BinaryElement,
        'DateElement': DateElement,
        'FloatElement': FloatElement,
        'IntegerElement': IntegerElement,
        'MasterElement': MasterElement,
        'StringElement': StringElement,
        'UIntegerElement': UIntegerElement,
        'UnicodeElement': UnicodeElement,
    }

    # Mapping of schema type names to the corresponding Element subclasses.
    # For python-ebml compatibility.
    ELEMENT_TYPES = {
        'integer': IntegerElement,
        'uinteger': UIntegerElement,
        'float': FloatElement,
        'string': StringElement,
        'utf-8': UnicodeElement,
        'date': DateElement,
        'binary': BinaryElement,
        'master': MasterElement,
    }
    

    def __init__(self, source, name=None):
        """ Constructor. Creates a new Schema from a schema description XML.
        
            @param source: The Schema's source, either a string with the full 
                path and name of the schema XML file, or a file-like stream.
            @keyword name: The schema's name. Defaults to the document type
                element's default value (if defined) or the base file name.
        """
        self.source = source
        self.filename = None
        
        if isinstance(source, basestring):
            self.filename = os.path.realpath(source)
        elif hasattr(source, "name"):
            self.filename = os.path.realpath(source.name)

        self.elements = {}    # Element types, keyed by ID
        self.elementsByName = {}  # Element types, keyed by element name
        self.elementInfo = {} # Raw element schema attributes, keyed by ID

        self.globals = {}   # Elements valid for any parent, by ID
        self.children = {}  # Valid root elements, by ID
        
        # Parse, using the correct method for the schema format.
        schema = ET.parse(source)
        root = schema.getroot()
        if root.tag == "table":
            # Old python-ebml schema: root element is <table>
            self._parseLegacySchema(root)
        elif root.tag == "Schema":
            # new ebmlite schema: root element is <Schema>
            self._parseSchema(root, self)
        else:
            raise IOError("Could not parse schema; expected root element "
                          "<Schema> or <table>, got <%s>" % root.tag)

        # Special case: `Void` is a standard EBML element, but not its own
        # type (it's technically binary). Use the special `VoidElement` type.
        if 'Void' in self.elementsByName:
            el = self.elementsByName['Void']
            void = type('VoidElement', (VoidElement,), 
                        {'id':el.id, 'name':'Void', 'schema':self, 
                         'mandatory': el.mandatory, 'multiple': el.multiple})
            self.elements[el.id] = void
            self.elementsByName['Void'] = void
        
        # Schema name. Defaults to the schema's default EBML 'DocType'
        self.name = name or self.type
        
        # Create the schema's Document subclass.
        self.document = type('%sDocument' % self.name.title(), (Document,),
                             {'schema': self})

    
    def _parseLegacySchema(self, schema):
        """ Parse a legacy python-ebml schema XML file.
        """
        for el in schema.findall('element'):
            attribs = el.attrib.copy()
            
            eid = int(attribs['id'],16) if 'id' in attribs else None
            ename = attribs['name'].strip() if 'name' in attribs else None
            etype = attribs['type'].strip() if 'type' in attribs else None

            # Use text in the element as its docstring. Note: embedded HTML tags
            # (as in the Matroska schema) will cause the text to be truncated.
            docs = el.text.strip() if isinstance(el.text, basestring) else None
            

            if etype is None:
                raise ValueError('Element "%s" (ID 0x%02X) missing required '
                                 '"type" attribute' % (ename, eid))
            
            if etype not in self.ELEMENT_TYPES:
                raise ValueError("Unknown type for element %r (ID 0x%02x): %r" %
                                 (ename, eid, etype))
            
            self.addElement(eid, ename, self.ELEMENT_TYPES[etype], attribs, 
                            docs=docs)


    def _parseSchema(self, el, parent=None):
        """ Recursively crawl a schema XML definition file.
        """
        if el.tag == "Schema":
            for chEl in el.getchildren():
                self._parseSchema(chEl, self)
            return
            
        if el.tag not in self.BASE_CLASSES:
            if el.tag.endswith('Element'):
                raise ValueError('Unknown element type: %s' % el.tag)
            
            # FUTURE: Add schema-describing metadata (author, origin,
            # description, etc.) to XML as non-Element elements. Parse them out
            # here.
            return
        
        attribs = el.attrib.copy()
        eid = int(attribs['id'],16) if 'id' in attribs else None
        ename = attribs['name'].strip() if 'name' in attribs else None
        
        # Use text in the element as its docstring. Note: embedded HTML tags
        # (as in the Matroska schema) will cause the text to be truncated.
        docs = el.text.strip() if isinstance(el.text, basestring) else None
        
        baseClass = self.BASE_CLASSES[el.tag]

        cls = self.addElement(eid, ename, baseClass, attribs, parent, docs)
        
        if baseClass is MasterElement:
            for chEl in el.getchildren():
                self._parseSchema(chEl, cls)
                

    def addElement(self, eid, ename, baseClass, attribs={}, parent=None,
                   docs=None):
        """ Create a new `Element` subclass and add it to the schema. 
        
            Duplicate elements are permitted (e.g. if one kind of element can 
            appear in different master elements), provided their attributes do 
            not conflict. The first appearance of an element definition in the
            schema must contain the required ID, name, and type; successive 
            appearances only need the ID and/or name.
        
            @param eid: The element's EBML ID.
            @param ename: The element's name.
            @param etype: The element's type (string, see `ELEMENT_TYPES`)
            @keyword multiple: If `True`, an EBML document can contain more
                than one of this element. Not currently enforced.
            @keyword mandatory: If `True`, a valid EBML document requires one 
                (or more) of this element. Not currently enforced.
            @keyword length: A fixed length to use when writing the element.
                `None` will use the minimum length required.
            @keyword precache: If `True`, the element's value will be read
                when the element is parsed, rather than when the value is
                explicitly accessed. Can save time for small elements.
            @keyword attribs: A dictionary of raw element attributes, as read
                from the schema file.
            @keyword parent: The new element's parent element class.
            @keyword docs: The new element's docstring (e.g. the defining XML
                element's text content).
        """
        
        def _getBool(d, k, default):
            " Helper function to get a dictionary value cast to bool. "
            try:
                return str(d[k]).strip()[0] in 'Tt1'
            except (KeyError, TypeError, IndexError, ValueError):
                # TODO: Don't fail silently for some exceptions.
                pass
            return default

        def _getInt(d, k, default):
            " Helper function to get a dictionary value cast to int. "
            try:
                return int(literal_eval(d[k].strip()))
            except (KeyError, SyntaxError, TypeError, ValueError):
                # TODO: Don't fail silently for some exceptions.
                pass
            return default
        
        if eid in self.elements or ename in self.elementsByName:
            # Already appeared in schema. Duplicates are permitted for defining
            # an element that can appear as a child to multiple Master elements,
            # so long as they have the same attributes. Additional definitions 
            # only need to specify the element ID and/or element name.
            oldEl = self[ename or eid]
            ename = oldEl.name
            eid = oldEl.id
            
            if not issubclass(self.elements[eid], baseClass):
                raise TypeError('%s %r (ID 0x%02X) redefined as %s' %
                                (oldEl.__name__, ename, eid, baseClass.__name__))
                
            newatts = self.elementInfo[eid].copy()
            newatts.update(attribs)
            if self.elementInfo[eid] == newatts:
                eclass = self.elements[eid]
            else:
                raise TypeError('Element %r (ID 0x%02X) redefined with '
                                'different attributes' % (ename, eid))
        else:
            # New element class. It requires both a name and an ID.
            # Validate both the name and the ID.
            if eid is None:
                raise ValueError('Element definition missing required '
                                 '"id" attribute')
            elif not isinstance(eid, (int, long)):
                raise TypeError("Invalid type for element ID: " + \
                                "{} ({})".format(eid, type(eid).__name__))

            if ename is None:
                raise ValueError('Element definition missing required '
                                 '"name" attribute')
            elif not isinstance(ename, basestring):
                raise TypeError('Invalid type for element name: ' + \
                                 '{} ({})'.format(ename, type(ename).__name__))
            elif not (ename[0].isalpha() or ename[0] == "_"):
                raise ValueError("Invalid element name: %r" % ename)
    
            mandatory = _getBool(attribs, 'mandatory', False)
            multiple = _getBool(attribs, 'multiple', False)
            precache = _getBool(attribs, 'precache', baseClass.precache)
            length = _getInt(attribs, 'length', None)
            level = _getInt(attribs, 'level', None)
            
            # Create a new Element subclass
            eclass = type('%sElement' % ename, (baseClass,),
                          {'id':eid, 'name':ename, 'schema':self,
                           'mandatory': mandatory, 'multiple': multiple, 
                           'precache': precache, 'length':length,
                           'children': dict(), '__doc__': docs})
                             
            self.elements[eid] = eclass
            self.elementInfo[eid] = attribs
            self.elementsByName[ename] = eclass
        
            # Element 'level'. EBMLite schemata explicitly define the hierarchy
            # (i.e. what elements are valid children), so only the value -1 has
            # any meaning: level -1 elements can appear anywhere in the file. 
            if level == -1:
                self.globals[eid] = eclass
                
        parent = parent or self.document
        if parent.children is None:
            parent.children = {}
        parent.children[eid] = eclass
        
        return eclass
        

    def __repr__(self):
        try:
            return "<%s %r from '%s'>" % (self.__class__.__name__, self.name,
                                          self.filename or self.source)
        except AttributeError:
            return object.__repr__(self)

    
    def __eq__(self, other):
        """ Equality check. Schemata are considered equal if the attributes of
            their elements match.
        """
        try:
            return self is other or self.elementInfo == other.elementInfo
        except AttributeError:
            return False


    def __contains__(self, key):
        """ Does the Schema contain a given element name or ID? """
        return (key in self.elementsByName) or (key in self.elements)
    
    
    def __getitem__(self, key):
        """ Get an Element class from the schema, by name or by ID. """
        
        try:
            self.elements[key]
        except KeyError:
            return self.elementsByName[key]


    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default


    def load(self, fp, name=None, headers=False, **kwargs):
        """ Load an EBML file using this Schema.
            
            @param fp: A file-like object containing the EBML to load, or the
                name of an EBML file.
            @keyword name: The name of the document. Defaults to filename.
            @keyword headers: If `False`, the file's ``EBML`` header element 
                (if present) will not appear as a root element in the document.
                The contents of the ``EBML`` element will always be read.  
        """
        if isinstance(fp, basestring):
            fp = open(fp, 'rb')

        return self.document(fp, name=name, headers=headers, **kwargs)


    def loads(self, data, name=None):
        """ Load EBML from a string using this Schema.
        
            @param data: A string or bytearray containing raw EBML data.
            @keyword name: The name of the document. Defaults to the Schema's
                document class name.
        """
        return self.load(StringIO(data), name=name)
        

    def __call__(self, fp, name=None):
        """ Load an EBML file using this Schema. Same as `Schema.load()`.
        
            @todo: Decide if this is worth keeping. It exists for historical
                reasons that may have been refactored out.
            
            @param fp: A file-like object containing the EBML to load, or the
                name of an EBML file.
            @keyword name: The name of the document. Defaults to filename.
        """
        return self.load(fp, name=name)


    #===========================================================================
    # Schema info stuff. Uses python-ebml schema XML data. Refactor later.
    #===========================================================================

    def _getInfo(self, eid, dtype):
        """ Helper method to get the 'default' value of an element. """
        try:
            return dtype(self.elementInfo[eid]['default'])
        except (KeyError, ValueError):
            return None


    @property
    def version(self):
        """ Schema version, extracted from EBML ``DocTypeVersion`` default. """
        return self._getInfo(0x4287, int) # ID of EBML 'DocTypeVersion'


    @property
    def type(self):
        """ Schema type name, extracted from EBML ``DocType`` default. """
        return self._getInfo(0x4282, str) # ID of EBML 'DocType'


    #===========================================================================
    # Encoding
    #===========================================================================
    
    def encode(self, stream, data, headers=False):
        """ Write an EBML document using this Schema to a file or file-like
            stream.
            
            @param stream: The file (or ``.write()``-supporting file-like 
                object) to which to write the encoded EBML.
            @param value: The data to encode, provided as a dictionary keyed by
                element name, or a list of two-item name/value tuples. Note: 
                individual items in a list of name/value pairs *must* be tuples!
        """ 
        self.document.encode(stream, data, headers=headers)
        return stream


    def encodes(self, data, headers=False):
        """ Create an EBML document using this Schema, returned as a string.
            
            @param value: The data to encode, provided as a dictionary keyed by
                element name, or a list of two-item name/value tuples. Note: 
                individual items in a list of name/value pairs *must* be tuples!
            @return: A string containing the encoded EBML binary.
        """ 
        stream = StringIO()
        self.encode(stream, data, headers=headers)
        return stream.getvalue()


    def verify(self, data):
        """ Perform basic tests on EBML binary data, ensuring it can be parsed
            using this `Schema`. Failure will raise an expression.
        """
        
        def _crawl(el):
            if isinstance(el, MasterElement):
                for subel in el:
                    _crawl(subel)
            elif isinstance(el, UnknownElement):
                raise NameError("Verification failed, unknown element ID %x" %
                                el.id)
            else:
                _ = el.value
                
            return True

        return _crawl(self.loads(data))
    

#===============================================================================
# 
#===============================================================================

def loadSchema(filename, reload=False, **kwargs):
    """ Import a Schema XML file. Loading the same file more than once will
        return the initial instantiation, unless `reload` is `True`.
        
        @param filename: The name of the Schema XML file. If the file cannot
            be found and file's path is not absolute, the paths listed in
            `SCHEMA_PATH` will be searched (similar to `sys.path` when importing
            modules).
        @keyword reload: If `True`, the resulting Schema is guaranteed to be
            new. Note: existing references to previous instances of the Schema
            and/or its elements will not update.
        
        Additional keyword arguments are sent verbatim to the `Schema`
        constructor.
    """
    global SCHEMATA
    
    origName = filename
    if not filename.startswith(('.','/','\\','~')):
        # Not a specific path and file not found: search paths in SCHEMA_PATH
        for p in SCHEMA_PATH:
            f = os.path.join(p, origName)
            if os.path.exists(f):
                filename = f
                break
    
    filename = os.path.realpath(os.path.expanduser(filename))
    if filename in SCHEMATA and not reload:
        return SCHEMATA[filename]
    
    if not os.path.exists(filename):
        raise IOError(errno.ENOENT, 'Could not find schema XML', origName)
    
    return SCHEMATA.setdefault(filename, Schema(filename, **kwargs))

