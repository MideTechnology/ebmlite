import argparse

from ebmlite.console_scripts import utils
import ebmlite.util


def parseArgs():
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

    return argparser.parse_args()


def run(filein, schema, fileout=None, clobber=True):
    with utils.load_files(
        filein, schema, fileout, clobber, binary_output=True
    ) as (schema, out):
        ebmlite.util.xml2ebml(filein, out, schema)  # , sizeLength=4, headers=True, unknown=True)


def main():
    run(**utils.formatArgs(parseArgs()))


if __name__ == "__main__":
    main()
