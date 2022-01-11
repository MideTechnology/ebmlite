import argparse

from ebmlite.tools import utils
import ebmlite.util


def main():
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

    with utils.load_files(args, binary_output=True) as (schema, out):
        ebmlite.util.xml2ebml(args.input, out, schema)  # , sizeLength=4, headers=True, unknown=True)


if __name__ == "__main__":
    main()
