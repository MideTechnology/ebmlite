.. travis
.. image:: https://api.travis-ci.org/MideTechnology/ebmlite.svg?branch=master

.. travis
.. image:: https://codecov.io/gh/MideTechnology/ebmlite/branch/master/graph/badge.svg



****************
*ebmlite* README
****************

*ebmlite* is a lightweight, "pure Python" library for parsing EBML (Extensible
Binary Markup Language) data. It is designed to crawl through EBML files quickly
and efficiently, and that's about it. *ebmlite* can also do basic EBML encoding,
but more advanced EBML manipulation (e.g. with a proper `DOM <https://en.wikipedia.org/wiki/Document_Object_Model>`_)
are beyond its scope, and are better left to other libraries.

*ebmlite* is currently a work-in-progress. It is usable (we use it extensively),
but does not (yet) implement the full EBML specification.

Parts of *ebmlite* were modeled after `python-ebml <https://github.com/jspiros/python-ebml>`_,
which we had previously been using, but is not a directly derivative work.
*ebmlite* can import *python-ebml* schemata XML (to a limited degree), but that
is the extent of its cross-compatibility.

EBML Overview (the short version)
=================================

`EBML <http://matroska-org.github.io/libebml/>`_  (Extensible Binary Markup
Language) is a hierarchical tagged binary format, originally created for the
`Matroska <https://www.matroska.org/>`_ project. The hierarchical structure of
EBML bears some conceptual/functional similarity to XML, although the actual
structure differs significantly.

In the raw, EBML elements consist of a numeric ID, the size of the element, and
a payload. It is space-efficient; the lengths of the ID and size descriptors are
variable, using prefix bits to indicate their lengths, a system similar to UTF-8.
The mapping of IDs to names and payload data types is done via an external schema.

See the `official specification <http://matroska-org.github.io/libebml/specs.html>`_
for more information.

EBML Schemata
=============

An EBML file is largely meaningless without a schema that defines its elements.
The schema maps element IDs to names and data types; it also describes the
structure (e.g. what elements can be children of other elements) and provides
additional metadata. *Note: ebmlite currently uses the structure for decoding
only, and does not stringently enforce it.*

*ebmlite* schemata are defined in XML. From these XML files, a :code:`Schema`
instance is created; within the :code:`Schema` are :code:`Element` subclasses
for each element defined in the XML. Since the interpretation of an EBML file is
almost entirely dependent on a schema, importing of EBML files is done through a
:code:`Schema` instance.

.. code-block:: python

    from ebmlite import loadSchema
    schema = loadSchema('mide_ide.xml')
    doc = schema.load('test_file.ebml')


*ebmlite* uses its own Schema definition syntax; it can also import python-ebml
schemata. It does not (currently) use the `official schema format
<https://github.com/Matroska-Org/ebml-specification/blob/master/specification.markdown#ebml-schema>`_.

Here is an example of an *ebmlite* schema, showing a simplified version of the
definition of the standard EBML header elements:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <Schema>
        <MasterElement name="EBML" id="0x1A45DFA3" mandatory="1" multiple="0">
            <UIntegerElement name="EBMLVersion" id="0x4286" multiple="0" mandatory="1" />
            <UIntegerElement name="EBMLReadVersion" id="0x42F7" multiple="0" mandatory="1"/>
            <UIntegerElement name="EBMLMaxIDLength" id="0x42F2" multiple="0" mandatory="1"/>
            <UIntegerElement name="EBMLMaxSizeLength" id="0x42F3" multiple="0" mandatory="1"/>
            <StringElement name="DocType" id="0x4282" multiple="0" mandatory="1"/>
            <UIntegerElement name="DocTypeVersion" id="0x4287" multiple="0" mandatory="1"/>
            <BinaryElement name="Void" global="1" id="0xEC" multiple="1"/>
            <BinaryElement name="CRC-32" global="1" id="0xBF" multiple="0"/>
            <MasterElement name="SignatureSlot" global="1" id="0x1B538667" multiple="1">
                <UIntegerElement name="SignatureAlgo" id="0x7E8A" multiple="0"/>
                <UIntegerElement name="SignatureHash" id="0x7E9A" multiple="0"/>
                <BinaryElement name="SignaturePublicKey" id="0x7EA5" multiple="0"/>
                <BinaryElement name="Signature" id="0x7EB5" multiple="0"/>
                <MasterElement name="SignatureElements" id="0x7E5B" multiple="0">
                    <MasterElement name="SignatureElementList" id="0x7E7B" multiple="1">
                        <BinaryElement name="SignedElement" id="0x6532" multiple="1"/>
                    </MasterElement>
                </MasterElement>
            </MasterElement>
        </MasterElement>
        <!-- More definitions would follow... -->
    </Schema>


Each element defined in the schema is a subclass of one of 8 Element base classes:

* **MasterElement:** An element containing other elements.
* **IntegerElement:** Contains a signed integer value of variable length.
* **UIntegerElement:** Contains an unsigned integer value of variable length.
* **FloatElement:** Contains a 32 or 64 bit floating point value.
* **StringElement:** Contains printable US-ASCII characters (0x20 to 0x7E).
* **UnicodeElement:** Contains UTF-8 string data.
* **DateElement:** Contains a timestamp, stored as nanoseconds since
  2001-01-01T00:00:00 UTC as a 64 bit integer. *ebmlite* automatically translates
  this into a Python :code:`datetime.datetime` object.
* **BinaryElement:** Contains binary data.

Element definitions have several attributes:

* :code:`name` (string): The Element subclass' name.
* :code:`id` (integer): The Element subclass' EBML ID.
* :code:`global` (bool, optional): If "true" (e.g. :code:`1` or :code:`True`),
  the element may appear in any location in an EBML file, not just where it
  appears in the schema. This is equivalent to a :code:`depth` of :code:`-1` in
  a *python-ebml* schema
* :code:`length` (integer, optional): A fixed size to use when encoding the
  element, overriding the EBML variable length encoding. Use to create
  byte-aligned structures.
* :code:`multiple` (bool, optional, default=1): Indicates that the element can
  appear more than once within the same parent.
  *Currently partially enforced for encoding.*
* :code:`mandatory` (bool, optional, default=0): Indicates that the element
  *must* be present. *Not currently enforced.*
* :code:`precache` (bool, optional, default varies by type): Indicates that the
  element's value should be read and cached when the element is parsed, rather
  than 'lazy-loaded' when explicitly accessed. Can be used to reduce the number
  of seeks when working with an EBML file after it has been imported. Simple
  numeric element types have this enabled by default; master, binary, and
  string/Unicode elements do not.

There are two additional, special-case Element subclasses which are not subclassed:

* **UnknownElement:** Instantiated for elements with IDs that do not appear in
  the schema. Its payload is treated as binary data. The UnknownElement itself
  does not appear in the Schema. Unlike other Element subclasses, its ID can
  vary from instance to instance.
* **VoidElement:** "Void" (ID :code:`0xEC`) is a standard EBML element,
  typically used for padding. If the Schema defines the Void element, it is
  replaced by this special-case element. The contents of its payload are ignored.

The structure of the schema's XML defines the structure of the EBML document;
children of a MasterElement in the schema are valid child element types in the EBML.
An Element type can appear multiple times in a schema; i.e. if its type can
appear as a child of different parent types. Only the first definition requires
both :code:`name` and :code:`id` attributes. Successive definitions can be
abbreviated to just the :code:`name` and/or :code:`id`; they will inherit all
the other attributes of the first definition. Successive definitions must *not*
have contradictory attributes, however.

.. code-block:: xml

    <Schema>
        <MasterElement name="Parent1" id="0x5210">
            <!-- first definition of child: has all attributes -->
            <IntegerElement name="SharedChild" id="0x5211" precache="1" length="8"/>
        </MasterElement>

        <!-- Proper reuse of a child element -->
        <MasterElement name="Parent2" id="0x5220">
            <!-- second definition of child: only name (preferred) or ID required -->
            <IntegerElement name="SharedChild"/>
        </MasterElement>
        <MasterElement name="Parent3" id="0x5230">
            <!-- third definition of child: only name (preferred) or ID required -->
            <IntegerElement id="0x5211"/>
        </MasterElement>

        <!-- A bad reuse! This will raise an exception when the schema is parsed. -->
        <MasterElement name="Parent3" id="0x5230">
            <!-- BAD REDEFINITION: attribute(s) contradict initial definition! -->
            <IntegerElement name="SharedChild" id="0xBAD1D"/>
        </MasterElement>
    </Schema>


**Note:** As seen in the example above, *ebmlite* allows an EBML document to
have multiple elements at its root level. Several other EBML libraries do this
as well, but this is apparently counter to the official spec. Officially, an EBML
document should have only a single root element, similar to an XML file.

*ebmlite*
=========

Schema
------

The :code:`Schema` class is a factory used to encode and decode EBML files.
When it's initialized, it scans through the schema file and creates a new class
for each element present in the file; then, when encoding or decoding files, it
references these classes in order to encapsulate everything safely.

Documents
---------

:code:`Documents` are subclasses of MasterElements, which act as an interface to
EBML files and act as the root node of the EBML tree.  Each :code:`Schema` also
creates a :code:`Document` subclass to use, and the base :code:`Document` class
will not function without class variables defined by the :code:`Schema`.

Utils
-----

The functions provided by util.py will expose the majority of functionality
needed to users, without the need to interface too deeply with this library.
The following functions are provided:

* | util. **toXml** (el, [parent= :code:`None`,] [offsets= :code:`True`,]
    [sizes= :code:`True`,] [types= :code:`True`,] [ids= :code:`True`]):
  | Recursively converts EBML elements into xml elements.
  | **Argument** *el*: an EBML element or document.
  | **Optional Argument** *parent*: The resulting XML element's parent element, if any.
  | **Optional Argument** *offsets*: If :code:`True`, create an :code:`offset`
    attributes for each generated XML element, containing the corresponding EBML
    element's offset.
  | **Optional Argument** *sizes*: If :code:`True`, create :code:`size`
    attributes containing the corresponding EBML element's size.
  | **Optional Argument** *types*: If :code:`True`, create :code:`type`
    attributes containing the name of the corresponding EBML element type.
  | **Optional Argument** *ids*: If :code:`True`, create :code:`id` attributes
    containing the corresponding EBML element's EBML ID.
  | **Returns**: the root of an XML tree created using the xml.etree.ElementTree
    built-in class.


* | util. **xmlElement2ebml**\(xmlEl, ebmlFile, schema, [sizeLength= :code:`4`,]
    [unknown= :code:`True`]):
  | Recursively converts XML elements tonight into EBML elements.
  | **Argument** *xmlEl*: The XML element. Its tag must match an element defined
    in the :code:`schema`.
  | **Argument** *ebmlFile*: An open file-like stream, to which the EBML data
    will be written.
  | **Argument** *schema*: An :code:`ebmlite.core.Schema` instance to use when
    writing the EBML document.
  | **Optional Argument** *sizeLength*:
  | **Optional Argument** *unknown*: If :code:`True`, unknown element names will
    be allowed, provided their XML elements include an :code:`id` attribute with
    the EBML ID (in hexadecimal).
  | **Returns**: the length of the encoded element, including header and children.
  | **Raises**: *NameError*: raised if an xml element is not present in the
    schema and unknown is False, OR if the xml element does not have an ID.


* | util. **xml2ebml**\(xmlFile, ebmlFile, schema, [sizeLength= :code:`4`,]
    [headers= :code:`True`,] [unknown= :code:`True`]):
  | **Argument** *xmlFile*: The XML source. Can be a filename, an open file-like
    stream, or a parsed XML document.
  | **Argument** *ebmlFile*: The EBML file to write. Can be a filename or an open
    file-like stream.
  | **Argument** *schema*: The EBML schema to use. Can be a filename or an instance
    of a :code:`Schema`.
  | **Optional Argument** *sizeLength*: The default length of each element's size
    descriptor. Must be large enough to store the largest 'master' element.  If
    an XML element has a :code:`sizeLength` attribute, it will override this.
  | **Optional Argument** *headers*: If :code:`True`, generate the standard
    :code:`EBML` EBML element if the XML document does not contain one.
  | **Optional Argument** *unknown*: If :code:`True`, unknown element names will
    be allowed, provided their XML elements include an :code:`id` attribute with
    the EBML ID (in hexadecimal).
  | **Returns**: the size of the ebml file in bytes.
  | **Raises**: NameError: raises if an xml element is not present in the schema.


* | util. **loadXml**\(xmlFile, schema, [ebmlFile= :code:`None`]):
  | Helpful utility to load an EBML document from an XML file.
  | **Argument** *xmlFile*: The XML source. Can be a filename, an open file-like
    stream, or a parsed XML document.
  | **Argument** *schema*: The EBML schema to use. Can be a filename or an
    instance of a :code:`Schema`.
  | **Optional Argument** *ebmlFile*: The name of the temporary EBML file to
    write, or :code:`:memory:` to use RAM (like :code:`sqlite3`). Defaults to an
    automatically-generated temporary file.
  | **Returns**: the root node of the specified EBML file


* | util. **pprint**:
  | Test function to recursively crawl an EBML document or element and print its
    structure, with child elements shown indented.
  | **Argument** *el*: An instance of a :code:`Document` or :code:`Element` subclass.
  | **Argument** *values*: If :code:`True`, show elements' values.
  | **Optional Argument** *out*: A file-like stream to which to write.
  | **Optional Argument** *indent*: The string containing the character(s) used
    for each indentation.

Utils can also be called from the command line with the following syntax:

.. code-block:: powershell

    python util.py {xml2ebml|ebml2xml|view} {FILE1.ebml|FILE1.xml} SCHEMA.xml [-o {FILE2.xml|FILE2.ebml}] [-c|--clobber] [-p|--pretty]

The program requires you to specify a mode: xml2ebml, ebml2xml, or view.  The first two modes convert xml files to ebml files and ebml files to xml files, respectively; the last mode formats an IDE file to be human-readable.
FILE1: The location of the ebml or xml file to convert/view.
SCHEMA: The location of the schema to use when interpreting these files.
FILE2: The location to output to; otherwise, the output is directed into the console.
-c|--clobber: If FILE2 exists, then overwrite it, otherwise the program will fail.
-p|--pretty: Prints the output in a human-readable format.


*****
To Do
*****

* Complete documentation and example code.
* See `@todo` items in the Python files (i.e. `core.py`).