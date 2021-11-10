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
        '-p', '--pretty', action="store_true", help="Generate 'pretty' XML.",
    )
    argparser.add_argument(
        '--min',
        action="store_true",
        help="Generate minimal XML with ebml2xml. Just element name and value",
    )

    args = argparser.parse_args()

    with utils.load_files(args, binary_output=not args.pretty) as (schema, out):
        doc = schema.load(args.input, headers=True)
        if args.min:
            root = ebmlite.util.toXml(doc, offsets=False, sizes=False, types=False, ids=False)
        else:
            root = ebmlite.util.toXml(doc)  # , offsets, sizes, types, ids)
        s = ET.tostring(root, encoding="utf-8")
        if args.pretty:
            parseString(s).writexml(out, addindent='\t', newl='\n', encoding='utf-8')
        else:
            out.write(s)


if __name__ == "__main__":
    main()
