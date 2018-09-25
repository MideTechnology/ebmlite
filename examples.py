# Imports from EBMLite
import core
from util import toXml, loadXml, xml2ebml, pprint

# imports from python's built in xml library
from xml.etree import ElementTree as ET
from xml.dom.minidom import parseString

# =======================================
# converting a file from EBML to XML
# =======================================

# Files to use in this example
schemaFile = '.\\schemata\\mide.xml'
ebmlFile1  = '.\\testFiles\\SSX46714-doesnot.IDE'
xmlFile1   = '.\\testFiles\\example-xml.xml'

# load the schema to use with these files.  This creates an object that is used
# to parse EBML files.
schema = core.loadSchema(schemaFile)

# Convert the EBML file to XML
ebmlDoc1   = schema.load(ebmlFile1, headers=True)       # load the file through
                                                        # the schema
ebmlRoot   = toXml(ebmlDoc1)                            # convert the file into
                                                        # a tree of XML elements
xmlString1 = ET.tostring(ebmlRoot, encoding='UTF-8')    # convert the xml tree
                                                        # into a string

# Save xml
with open(xmlFile1, 'wt') as f:
    # convert the xml string into a minidom object and pretty-print
    f.write(parseString(xmlString1).toprettyxml(indent='    '))

# =======================================
# converting a file from XML to EBML
# =======================================

# Files to use in this example
schemaFile = '.\\schemata\\mide.xml'
ebmlFile1  = '.\\testFiles\\example-ebml.ide'
xmlFile1   = '.\\testFiles\\example-xml.xml'

# load the schema to use with these files.  This creates an object that is used
# to parse EBML files.
schema = core.loadSchema(schemaFile)

# Convert the XML file to an EBML file on the disk
xml2ebml(xmlFile1, ebmlFile1, schema)

# Load the XML file into memory as an ebmlite.core.Document object
xmlDoc1 = loadXml(xmlFile1, schema)

# =======================================
# print an EBML file in a human-readable format
# =======================================

# Files to use in this example
schemaFile = '.\\schemata\\mide.xml'
ebmlFile1  = '.\\testFiles\\example-ebml.ide'
prettyXml  = '.\\testFiles\\example-pretty.txt'

# load the schema to use with these files.  This creates an object that is used
# to parse EBML files.
schema = core.loadSchema(schemaFile)

# load the ebml file into memory
ebmlDoc1 = schema.load(ebmlFile1, headers=True) # load the file through the schema

# save the ebml to an easily readable format
pprint(ebmlDoc1, out=open(prettyXml, 'wt'))

# =======================================
# Get specific data from an EBML file
# =======================================

# Files to use in this example
schemaFile = '.\\schemata\\mide.xml'
ebmlFile1  = '.\\testFiles\\example-ebml.ide'

# load the schema to use with these files.  This creates an object that is used
# to parse EBML files.
schema = core.loadSchema(schemaFile)

# load the ebml file into memory
ebmlDoc1 = schema.load(ebmlFile1, headers=True) # load the file through the schema

# convert ebml into an ordered dict
ebmlDict = ebmlDoc1.dump()

# extract recording properties from EBML
recProp = ebmlDict['RecordingProperties']

# extract recorder info from recording properties
recInfo = recProp['RecorderInfo']

# extract recorder serial number from recording properties
recSerial = recInfo['RecorderSerial']
print 'recorder serial number: %d' % recSerial