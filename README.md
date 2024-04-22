[![PyPI Latest Release](https://img.shields.io/pypi/v/ebmlite.svg)](https://pypi.org/project/ebmlite/) ![example workflow](https://github.com/MideTechnology/ebmlite/actions/workflows/unit-tests.yml/badge.svg) [![codecov](https://codecov.io/gh/MideTechnology/ebmlite/branch/master/graph/badge.svg)](https://codecov.io/gh/MideTechnology/ebmlite) 



_ebmlite_ README
================

_ebmlite_ is a lightweight, "pure Python" library for parsing EBML (Extensible Binary Markup Language) data. It is designed to crawl through EBML files quickly and efficiently, and that's about it. _ebmlite_ can also do basic EBML encoding, but more advanced EBML manipulation (e.g. with a proper [DOM](https://en.wikipedia.org/wiki/Document_Object_Model)) are beyond its scope, and are better left to other libraries.

_ebmlite_ is currently a work-in-progress. It is usable (we use it extensively), but does not (yet) implement the full EBML specification.

Parts of _ebmlite_ were modeled after [python-ebml](https://github.com/jspiros/python-ebml), which we had previously been using, but is not a directly derivative work. _ebmlite_ can import _python-ebml_ schemata XML (to a limited degree), but that is the extent of its cross-compatibility.

EBML Overview (the short version)
---------------------------------

[EBML](http://matroska-org.github.io/libebml/)  (Extensible Binary Markup Language) is a hierarchical tagged binary format, originally created for the [Matroska](https://www.matroska.org/) project. The hierarchical structure of EBML bears some conceptual/functional similarity to XML, although the actual structure differs significantly.

In the raw, EBML elements consist of a numeric ID, the size of the element, and a payload. It is space-efficient; the lengths of the ID and size descriptors are variable, using prefix bits to indicate their lengths, a system similar to UTF-8. The mapping of IDs to names and payload data types is done via an external schema.

See the [official specification](http://matroska-org.github.io/libebml/specs.html) for more information.

EBML Schemata
-------------

An EBML file is largely meaningless without a schema that defines its elements. The schema maps element IDs to names and data types; it also describes the structure (e.g. what elements can be children of other elements) and provides additional metadata. *Note: ebmlite currently uses the structure for decoding only, and does not stringently enforce it.*

_ebmlite_ schemata are defined in XML. From these XML files, a `Schema` instance is created; within the `Schema` are `Element` subclasses for each element defined in the XML. Since the interpretation of an EBML file is almost entirely dependent on a schema, importing of EBML files is done through a `Schema` instance.

```python
from ebmlite import loadSchema
schema = loadSchema('mide_ide.xml')
doc = schema.load('test_file.ebml')
```

_ebmlite_ uses its own Schema definition syntax; it can also import python-ebml schemata. It does not (currently) use the [official schema format](https://github.com/Matroska-Org/ebml-specification/blob/master/specification.markdown#ebml-schema).

Here is an example of an _ebmlite_ schema, showing a simplified version of the definition of the standard EBML header elements:
```xml
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
```

Each element defined in the schema is a subclass of one of 8 Element base classes:
* **MasterElement:** An element containing other elements.
* **IntegerElement:** Contains a signed integer value of variable length.
* **UIntegerElement:** Contains an unsigned integer value of variable length.
* **FloatElement:** Contains a 32 or 64 bit floating point value.
* **StringElement:** Contains printable US-ASCII characters (0x20 to 0x7E).
* **UnicodeElement:** Contains UTF-8 string data.
* **DateElement:** Contains a timestamp, stored as nanoseconds since 2001-01-01T00:00:00 UTC as a 64 bit integer. _ebmlite_ automatically translates this into a Python `datetime.datetime` object.
* **BinaryElement:** Contains binary data.

Element definitions have several attributes:
* `name` (string): The Element subclass' name.
* `id` (integer): The Element subclass' EBML ID.
* `global` (bool, optional): If "true" (e.g. `1` or `True`), the element may
appear in any location in an EBML file, not just where it appears in the
schema. This is equivalent to a `depth` of `-1` in a _python-ebml_ schema
* `length` (integer, optional): A fixed size to use when encoding the element, overriding the EBML variable length encoding. Use to create byte-aligned structures.
* `multiple` (bool, optional, default=1): Indicates that the element can appear more than once within the same parent. *Currently partially enforced for encoding.*
* `mandatory` (bool, optional, default=0): Indicates that the element *must* be present. *Not currently enforced.*
* `precache` (bool, optional, default varies by type): Indicates that the element's value should be read and cached when the element is parsed, rather than 'lazy-loaded' when explicitly accessed. Can be used to reduce the number of seeks when working with an EBML file after it has been imported. Simple numeric element types have this enabled by default; master, binary, and string/Unicode elements do not.

There are two additional, special-case Element subclasses which are not subclassed:
* **UnknownElement:** Instantiated for elements with IDs that do not appear in the schema. Its payload is treated as binary data. The UnknownElement itself does not appear in the Schema. Unlike other Element subclasses, its ID can vary from instance to instance.
* **VoidElement:** "Void" (ID `0xEC`) is a standard EBML element, typically used for padding. If the Schema defines the Void element, it is replaced by this special-case element. The contents of its payload are ignored.

The structure of the schema's XML defines the structure of the EBML document; children of a MasterElement in the schema are valid child element types in the EBML. An Element type can appear multiple times in a schema; i.e. if its type can appear as a child of different parent types. Only the first definition requires both `name` and `id` attributes. Successive definitions can be abbreviated to just the `name` and/or `id`; they will inherit all the other attributes of the first definition. Successive definitions must *not* have contradictory attributes, however.
```XML
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
```

**Note:** As seen in the example above, _ebmlite_ allows an EBML document to have multiple elements at its root level. Several other EBML libraries do this as well, but this is apparently counter to the official spec. Officially, an EBML document should have only a single root element, similar to an XML file.

Using Schema Files
------------------
### Schema File Location (`ebmlite.SCHEMA_PATH`)
`ebmlite.SCHEMA_PATH` is a list that stores a set of paths which will be searched for schema files, similar to
`sys.path` works for modules. If a schema filename with no path is used (e.g. `ebmlite.loadSchema("matroska.xml")`),
it is searched for in `SCHEMA_PATH`'s paths. Users may modify `SCHEMA_PATH` as needed.

The default schemata XML files are in the package's `schemata` subdirectory.

### Module-relative Paths
Since multiple packages are currently using `ebmlite`, schemata may be imported using module names. Modules
can be specified in paths by using braces (curly brackets) around their names (e.g., `"{idelib}/schemata/mide_ide.xml"`).
Module-relative names may be used when loading schemata, can be included in `ebmlite.SCHEMA_PATH`, and can be
used with the command-line utilities (in quotes).

_New to version 3.3._

### The `EBMLITE_SCHEMA_PATH` Environment Variable
An operating system environment variable may be defined as a global means of specifying schema paths, in and out
of Python. `EBMLITE_SCHEMA_PATH` functions like the `PATH` environment variable in Windows. `EBMLITE_SCHEMA_PATH`
contains one or more paths, which will be added to `ebmlite.SCHEMA_PATH`; multiple paths are delimited by `;` in
Windows, `:` in *NIX operating systems (Linux, macOS, etc.). `EBMLITE_SCHEMA_PATH` is largely intended for use
with the `ebmlite` command-line utilities.

_New to version 3.3._


_ebmlite_
----------------
### Schema
The ``Schema`` class is a factory used to encode and decode EBML files.  When it's initialized, it scans through the schema file and creates a new class for each element present in the file; then, when encoding or decoding files, it references these classes in order to encapsulate everything safely.  

### Documents
``Documents`` are subclasses of MasterElements, which act as an interface to EBML files and act as the root node of the EBML tree.  Each ``Schema`` also creates a ``Document`` subclass to use, and the base ``Document`` class will not function without class variables defined by the ``Schema``.  

### Utilities
The functions provided by util.py will expose the majority of functionality needed to users, without the need to interface too deeply with this library.  The following functions are provided:
* util.**toXml**(el, [parent=``None``,] [offsets=``True``,] [sizes=``True``,] [types=``True``,] [ids=``True``]):   
Recursively converts EBML elements into xml elements.    
Argument *el*: an EBML element or document.  
Optional argument *parent*: The resulting XML element's parent element, if any.  
Optional argument *offsets*: If `True`, create an ``offset`` attributes for
        each generated XML element, containing the corresponding EBML element's
        offset.   
Optional argument *sizes*: If `True`, create ``size`` attributes containing the
        corresponding EBML element's size.  
Optional argument *types*: If `True`, create ``type`` attributes containing the
        name of the corresponding EBML element type.  
Optional argument *ids*: If `True`, create ``id`` attributes containing the
        corresponding EBML element's EBML ID.      
Returns the root of an XML tree created using the xml.etree.ElementTree
        built-in class.  


* util.**xmlElement2ebml**(xmlEl, ebmlFile, schema, [sizeLength=4,] [unknown=True]):  
Recursively converts XML elements tonight into EBML elements.   
Argument *xmlEl*: The XML element. Its tag must match an element defined in the
        `schema`.   
Argument *ebmlFile*: An open file-like stream, to which the EBML data will be
        written.   
Argument *schema*: An `ebmlite.core.Schema` instance to use when writing the
        EBML document.    
Optional argument *sizeLength*:    
Optional argument *unknown*: If `True`, unknown element names will be allowed,
        provided their XML elements include an ``id`` attribute with the EBML
        ID (in hexadecimal).  
Returns the length of the encoded element, including header and children.   
Raises *NameError*: raised if an xml element is not present in the schema and
        unknown is False, OR if the xml element does not have an ID.   


* util.**xml2ebml**(xmlFile, ebmlFile, schema, [sizeLength=4,] [headers=True,] [unknown=True]):
Argument *xmlFile*: The XML source. Can be a filename, an open file-like
        stream, or a parsed XML document.   
Argument *ebmlFile*: The EBML file to write. Can be a filename or an open
        file-like stream.   
Argument *schema*: The EBML schema to use. Can be a filename or an instance of
        a `Schema`.   
Optional argument *sizeLength*: The default length of each element's size
        descriptor. Must be large enough to store the largest 'master' element.
        If an XML element has a ``sizeLength`` attribute, it will override
        this.   
Optional argument *headers*: If `True`, generate the standard ``EBML`` EBML
        element if the XML document does not contain one.   
Optional argument *unknown*: If `True`, unknown element names will be allowed,
        provided their XML elements include an ``id`` attribute with the EBML
        ID (in hexadecimal).   
Returns the size of the ebml file in bytes.   
Raises NameError: raises if an xml element is not present in the schema.


* util.**loadXml**(xmlFile, schema, [ebmlFile=``None``]):    
Helpful utility to load an EBML document from an XML file.    
Argument *xmlFile*: The XML source. Can be a filename, an open file-like
        stream, or a parsed XML document.   
Argument *schema*: The EBML schema to use. Can be a filename or an instance of
        a `Schema`.   
Optional Argument *ebmlFile*: The name of the temporary EBML file to write, or
        ``:memory:`` to use RAM (like `sqlite3`). Defaults to an
        automatically-generated temporary file.   
Returns the root node of the specified EBML file


* util.**pprint**:    
Test function to recursively crawl an EBML document or element and print its
        structure, with child elements shown indented.    
Argument *el*: An instance of a `Document` or `Element` subclass.    
Argument *values*: If `True`, show elements' values.    
Optional Argument *out*: A file-like stream to which to write.    
Optional argument *indent*: The string containing the character(s) used for each
        indentation.

Command Line Utilities
----------------------
When `ebmlite` is installed as a Python library, the utilities can be called from the command line.
From the command line, documentation can be viewed using one of the following:
```commandline
python -m ebmlite.tools.ebml2xml -h
python -m ebmlite.tools.xml2ebml -h
python -m ebmlite.tools.view_ebml -h
```
The commands available are:
### ebml2xml
```
python -m ebmlite.tools.ebml2xml <EBML file> <schema> -o <file.XML>
```
`ebml2xml` will translate an EBML file into XML. For example:
```commandline
python -m ebmlite.tools.ebml2xml DAQ11093_000001.ide mide_ide.xml -o DAQ11093_000001.xml
```
will translate the EBML file `DAQ11093_000001.ide` (an enDAQ data recorder file) into XML,
and write the result into `DAQ11093_000001.xml`. The schema `mide_ide.xml` is built in to
the EBMLite library.

### xml2ebml
```
python -m ebmlite.tools.xml2ebml <file.XML> <schema> -o <EBML file>
```
`xml2ebml` will translate XML back in to EBML. For example
```commandline
python -m ebmlite.tools.xml2ebml DAQ11093_000001.xml mide_ide.xml -o DAQ11093_000001b.ide
```
Will turn `DAQ11093_000001.xml` back into an IDE file.

### view_ebml
```
python -m ebmlite.tools.view_ebml <EBML file> <schema>
```
`view_ebml` will show summary element data about an EBML file, including element ID and type


### list_schemata
```
python -m ebmlite.tools.list_schemata
```
`list_schemata` will list all `ebmlite` schemata XML files in the directories specified in `ebmlite.SCHEMA_PATH`
(and the `EBMLITE_SCHEMA_PATH` OS environment variable, if defined). The resulting list displays the base filename
of the schema, followed by the file's full path, as well as the full paths of any schemata in other
directories/modules that share the base name. If the schema's base name is used without a path, the first file
will be loaded.

_New to version 3.3._

To Do
=====
* Complete documentation and example code.
* See `todo` items in the Python files (i.e. `core.py`).
