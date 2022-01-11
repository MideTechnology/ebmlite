import argparse
from xml.dom.minidom import parseString
from xml.etree import ElementTree as ET

from ebmlite.tools import utils
import ebmlite.util


def main():
    argparser = argparse.ArgumentParser(
        description="A tool for converting ebml to xml."
    )
    argparser.add_argument(
        'input', metavar="FILE.ebml", help="The source EBML file.",
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
    argparser.add_argument(
        '-s', '--single', action="store_true", help="Generate XML as a single line with no newlines or indents",
    )
    argparser.add_argument(
        '-m', '--max',
        action="store_true",
        help="Generate XML with maximum description, including offset, size, type, and id info",
    )
    argparser.add_argument(
        '-l', '--list', action="store_true",
        help="Display a list of EBML schemata found in SCHEMA_PATH",
    )
    argparser.add_argument(
        '-L', '--list_relative', action="store_true",
        help="Display a list of EBML schemata found in SCHEMA_PATH, using package-relative filenames",
    )

    args = argparser.parse_args()

    if args.list:
        ebmlite.util.printSchemata(args.output, absolute=not args.list_relative)
        exit(0)

    with utils.load_files(args, binary_output=args.single) as (schema, out):
        doc = schema.load(args.input, headers=True)
        if args.max:
            root = ebmlite.util.toXml(doc, offsets=True, sizes=True, types=True, ids=True)
        else:
            root = ebmlite.util.toXml(doc, offsets=False, sizes=False, types=False, ids=False)
        s = ET.tostring(root, encoding="utf-8")
        if args.single:
            out.write(s)
        else:
            parseString(s).writexml(out, addindent='\t', newl='\n', encoding='utf-8')


if __name__ == "__main__":
    main()
