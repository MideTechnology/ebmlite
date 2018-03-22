*ebmlite* README
==============

*ebmlite* is a lightweight, "pure Python" library for parsing EBML (Extensible Binary Markup Language) data. It is designed to crawl through EBML files quickly and efficiently, and that's about it. *ebmlite* can also do basic EBML encoding, but more advanced EBML manipulation (e.g. with a proper DOM) are beyond its scope, and are better left to other libraries.

EBML Overview (the short version)
---------------------------------

[EBML](http://matroska-org.github.io/libebml/)  (Extensible Binary Markup Language) is a hierarchical tagged binary format. It bears some functional similarity to XML, although the actual structure differs significantly.

In the raw, EBML elements consist of a numeric ID, the size of the element, and a payload. The lengths of the ID and size descriptors are variable, using prefix bits to indicate their lengths, a system similar to UTF-8. The mapping of IDs to names and payload data types is done via an external schema.

See the [official specification](http://matroska-org.github.io/libebml/specs.html) for more information.

EBML Schemata
-------------

An EBML file is largely meaningless without a schema that defines its elements. The schema maps element IDs to names and data types; it also describes the structure (e.g. what elements can be children of other elements) and provides additional metadata. *Note: ebmlite does not currently enforce structure.*

*ebmlite* schemata are defined in XML. From these XML files, a `Schema` instance is created; within the `Schema` are `Element` subclasses for each element defined in the XML. Since the interpretation of an EBML file is almost entirely dependent on a schema, importing of EBML files is done through a `Schema` instance.

```python
from ebmlite import loadSchema
schema = loadSchema('mide.xml')
doc = schema.load('test_file.ebml')
```

_ebmlite_ (currently) uses its own Schema definition syntax. It does not use the [official schema format](https://github.com/Matroska-Org/ebml-specification/blob/master/specification.markdown#ebml-schema).

Here is an example, showing a simplified version of the schema definition of the standard EBML header elements:
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
        <BinaryElement name="Void" level="-1" id="0xEC" multiple="1"/>
        <BinaryElement name="CRC-32" level="-1" id="0xBF" multiple="0"/>
        <MasterElement name="SignatureSlot" level="-1" id="0x1B538667" multiple="1">
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
* **StringElement:** Contains printable ASCII characters.
* **UnicodeElement:** Contains UTF-8 string data.
* **DateElement:** Contains a timestamp, stored as nanoseconds since 2001-01-01T00:00:00 UTC as a 64 bit integer. *ebmlite* automatically translates this into a Python `datetime.datetime` object.
* **BinaryElement:** Contains binary data.

Element definitions have several attributes:
* `name` (string): The Element subclass' name.
* `id` (integer): The Element subclass' EBML ID.
* `length` (integer, optional): A fixed size to use when encoding the element, overriding the EBML variable length encoding. Use to create byte-aligned structures.
* `level` (integer, optional): The allowed 'depth' of the element. Only the value `-1` has an effect in an *ebmlite* schema; it indicates that the element can appear anywhere in an EBML file.
* `multiple` (bool, optional, default=1): Indicates that the element can appear more than once within the same parent.
* `mandatory` (bool, optional, default=0): Indicates that the element *must* be present. *Not currently enforced.*
* `precache` (bool, optional, default varies by type): Indicates that the element's value should be read and cached when the element is parsed, rather than 'lazy-loaded' when explicitly accessed. Can be used to reduce the number of seeks when working with an EBML file after it has been imported. Simple numeric element types have this enabled by default; master, binary, and string/Unicode elements do not.

There are two additional, special-case Element subclasses which are not subclassed:
* **UnknownElement:** Instantiated for elements with IDs that do not appear in the schema. Its payload is treated as binary data. The UnknownElement itself does not appear in the Schema.
* **VoidElement:** "Void" (ID 0xEC) is a standard EBML element used for padding. If the Schema defines the Void element, it is replaced by this special-case element. The contents of its payload are ignored.

An Element type can appear multiple times in a schema; i.e. if its type can appear as a child of different parent types. Only the first definition requires both `name` and `id` attributes. Successive definitions can be abbreviated to just the `name` and/or `id`; they will inherit all the other attributes of the first definition. Successive definitions must *not* have contradictory attributes, however.
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

To Do
=====
* See `@todo` items in the Python files.
