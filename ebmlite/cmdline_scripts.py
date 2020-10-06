import contextlib
import sys
from xml.etree import ElementTree as ET

from . import core, util

import argparse
import os.path
from xml.dom.minidom import parseString


###############################################################################
# Utilities

def errPrint(msg):
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()
    exit(1)


@contextlib.contextmanager
def load_files(args):
    if not os.path.exists(args.input):
        sys.stderr.write("Input file does not exist: %s\n" % args.input)
        exit(1)

    try:
        schema = core.loadSchema(args.schema)
    except IOError as err:
        errPrint("Error loading schema: %s\n" % err)

    if not args.output:
        yield (schema, sys.stdout)
        return

    output = os.path.realpath(os.path.expanduser(args.output))
    if os.path.exists(output) and not args.clobber:
        errPrint("Output file exists: %s" % args.output)
    with open(output, 'wb') as out:
        yield (schema, out)


###############################################################################
# Command-Line Functions

def ebml2xml():
    argparser = argparse.ArgumentParser(
        description="A tool for converting ebml to xml."
    )
    argparser.add_argument(
        'schema',
        metavar="SCHEMA.xml",
        help=(
          "The name of the schema file. Only the name itself is required if"
          " the schema file is in the standard schema directory."
        ),
    )
    argparser.add_argument(
        'input', metavar="FILE.ebml", help="The source EBML file.",
    )
    argparser.add_argument(
        '-o', '--output', metavar="FILE.xml", help="The output file.",
    )
    argparser.add_argument(
        '-c', '--clobber', action="store_true",
        help="Clobber (overwrite) existing files.",
    )
    argparser.add_argument(
        '-p', '--pretty', action="store_true", help="Generate 'pretty' XML.",
    )
    argparser.add_argument(
        '--min',
        action="store_true",
        help="Generate minimal XML with ebml2xml. Just element name and value",
    )

    args = argparser.parse_args()

    with load_files(args) as (schema, out):
        doc = schema.load(args.input, headers=True)
        if args.min:
            root = util.toXml(doc, offsets=False, sizes=False, types=False, ids=False)
        else:
            root = util.toXml(doc)  # , offsets, sizes, types, ids)
        s = ET.tostring(root, encoding="utf-8")
        if args.pretty:
            parseString(s).writexml(out, addindent='\t', newl='\n', encoding='utf-8')
        else:
            out.write(s)


def xml2ebml():
    argparser = argparse.ArgumentParser(
        description="A tool for converting xml to ebml."
    )
    argparser.add_argument(
        'input', metavar="FILE.xml", help="The source XML file.",
    )
    argparser.add_argument(
        'schema',
        metavar="SCHEMA.xml",
        help=(
          "The name of the schema file. Only the name itself is required if"
          " the schema file is in the standard schema directory."
        ),
    )
    argparser.add_argument(
        '-o', '--output', metavar="FILE.ebml", help="The output file.",
    )
    argparser.add_argument(
        '-c', '--clobber', action="store_true",
        help="Clobber (overwrite) existing files.",
    )
    args = argparser.parse_args()

    with load_files(args) as (schema, out):
        util.xml2ebml(args.input, out, schema)  # , sizeLength=4, headers=True, unknown=True)


def view_ebml():
    argparser = argparse.ArgumentParser(
        description="A tool for reading ebml file content."
    )
    argparser.add_argument(
        'input', metavar="FILE.ebml", help="The source XML file.",
    )
    argparser.add_argument(
        'schema',
        metavar="SCHEMA.xml",
        help=(
          "The name of the schema file. Only the name itself is required if"
          " the schema file is in the standard schema directory."
        ),
    )
    argparser.add_argument(
        '-o', '--output', metavar="FILE.xml", help="The output file.",
    )
    argparser.add_argument(
        '-c', '--clobber', action="store_true",
        help="Clobber (overwrite) existing files.",
    )
    args = argparser.parse_args()

    with load_files(args) as (schema, out):
        doc = schema.load(args.input, headers=True)
        util.pprint(doc, out=out)
