.. ebmlite documentation master file, created by
   sphinx-quickstart on Wed Jul  8 15:45:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. default-domain:: py
.. currentmodule:: ebmlite.core

`ebmlite`
=========

*ebmlite* is a lightweight, "pure Python" library for parsing EBML (Extensible
Binary Markup Language) data. It is designed to crawl through EBML files quickly
and efficiently, and that's about it. *ebmlite* can also do basic EBML encoding,
but more advanced EBML manipulation (e.g. with a proper `DOM <https://en.wikipedia.org/wiki/Document_Object_Model>`_)
are beyond its scope, and are better left to other libraries.


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

The :class:`Schema` class is a factory used to encode and decode EBML files.
When it's initialized, it scans through the schema file and creates a new class
for each element defined in the schema file; then, when encoding or decoding EBML
files, it references these classes in order to encapsulate everything safely.

*ebmlite* schemata are defined in XML. From these XML files, a :class:`Schema`
instance is created; within the :class:`Schema` are :class:`Element` subclasses
for each element defined in the XML. Since the interpretation of an EBML file is
almost entirely dependent on a schema, importing of EBML files is done through a
:class:`Schema` instance.

:class:`Schema` instances are typically created from an XML file through :func:`loadSchema`,
or from a byte string using :func:`parseSchema`.

.. code-block:: python

    from ebmlite import loadSchema
    schema = loadSchema('mide_ide.xml')
    doc = schema.load('test_file.ebml')

Loading an EBML file creates an instance of a :class:`Document` subclass, created
by the schema, which acts as the root node of the EBML tree. :class:`Document`
instances are typically created by reading an EBML file with
:meth:`Schema.load`, or a  byte string via :meth:`Schema.loads`.

Schema Format
-------------
*ebmlite* uses its own Schema definition syntax. It does not (currently) use the `official schema format
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

Element types
'''''''''''''
Each element defined in the schema is a subclass of one of 8 Element base classes:

* **MasterElement:** An element containing other elements.
* **IntegerElement:** Contains a signed integer value of variable length.
* **UIntegerElement:** Contains an unsigned integer value of variable length.
* **FloatElement:** Contains a 32 or 64 bit floating point value.
* **StringElement:** Contains printable US-ASCII characters (0x20 to 0x7E).
* **UnicodeElement:** Contains UTF-8 string data.
* **DateElement:** Contains a timestamp, stored as nanoseconds since
  2001-01-01T00:00:00 UTC as a 64 bit integer. *ebmlite* automatically translates
  this into a Python :py:class:`datetime.datetime` object.
* **BinaryElement:** Contains binary data.

Element definitions have several attributes:

* :code:`name` (string): The Element subclass' name.
* :code:`id` (integer): The Element subclass' EBML ID.
* :code:`global` (bool, optional): If "true" (e.g. :code:`1` or :code:`True`),
  the element may appear in any location in an EBML file, not just where it
  appears in the schema.
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

Schema XML Structure
--------------------
The structure of the schema's XML defines the structure of the EBML document;
children of a MasterElement in the schema are valid child element types in the EBML.
An Element type can appear multiple times in a schema; i.e. if its type can
appear as a child of different parent types. Only the first definition requires
both :code:`name` and :code:`id` attributes. Successive definitions can be
abbreviated to just the :code:`name` and/or :code:`id`; they will inherit all
the other attributes of the first definition. Successive definitions must *not*
have contradictory attributes, however.

.. code-block:: xml

    <Schema name="Example2" version="1" readversion="1">
        ...
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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
