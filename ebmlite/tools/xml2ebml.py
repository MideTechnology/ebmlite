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
        '-n', '--no_header', action="store_true",
        help="Do not write the standard EBML header segment.",
    )
    args = argparser.parse_args()

    header = not args.no_header     # Removing some naming confusion, if no_header=false, header argument should be true
    with utils.load_files(args, binary_output=True) as (schema, out):
        ebmlite.util.xml2ebml(args.input, out, schema, headers=header)  # , sizeLength=4, headers=True, unknown=True)


if __name__ == "__main__":
    main()
