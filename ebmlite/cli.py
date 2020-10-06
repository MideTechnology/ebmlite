import contextlib
import sys
from xml.etree import ElementTree as ET

import ebmlite

import argparse
import os.path
from xml.dom.minidom import parseString


###############################################################################
# Utilities

def errPrint(msg):
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()
    exit(1)


def add_common_argparser_params(argparser):
    argparser.add_argument(
        'input',
        metavar="[FILE.ebml|FILE.xml]",
        help="The source file: XML for 'xml2ebml,' EBML for 'ebml2xml' or 'view.'",
    )
    argparser.add_argument(
        'schema',
        metavar="SCHEMA.xml",
        help=(
          "The name of the schema file. Only the name itself is required if the "
          "schema file is in the standard schema directory."
        ),
    )
    argparser.add_argument(
        '-o', '--output',
        metavar="[FILE.xml|FILE.ebml]",
        help="The output file.",
    )
    argparser.add_argument(
        '-c', '--clobber',
        action="store_true",
        help="Clobber (overwrite) existing files.",
    )

    return argparser


@contextlib.contextmanager
def load_files(args):
    if not os.path.exists(args.input):
        sys.stderr.write("Input file does not exist: %s\n" % args.input)
        exit(1)

    try:
        schema = ebmlite.core.loadSchema(args.schema)
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
    add_common_argparser_params(argparser)
    argparser.add_argument(
        '-p', '--pretty',
        action="store_true",
        help="Generate 'pretty' XML with ebml2xml.",
    )
    args = argparser.parse_args()

    with load_files(args) as (schema, out):
        doc = schema.load(args.input, headers=True)
        root = ebmlite.util.toXml(doc)  # , offsets, sizes, types, ids)
        s = ET.tostring(root, encoding="utf-8")
        if args.pretty:
            parseString(s).writexml(out, addindent=b'\t', newl=b'\n', encoding=b'utf-8')
        else:
            out.write(s)


def xml2ebml():
    argparser = argparse.ArgumentParser(
        description="A tool for converting xml to ebml."
    )
    add_common_argparser_params(argparser)
    args = argparser.parse_args()

    with load_files(args) as (schema, out):
        xml2ebml(args.input, out, schema)  # , sizeLength=4, headers=True, unknown=True)


def view_ebml():
    argparser = argparse.ArgumentParser(
        description="A tool for reading ebml file content."
    )
    add_common_argparser_params(argparser)
    args = argparser.parse_args()

    with load_files(args) as (schema, out):
        doc = schema.load(args.input, headers=True)
        ebmlite.util.pprint(doc, out=out)
