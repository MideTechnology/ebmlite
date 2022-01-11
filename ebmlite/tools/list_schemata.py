"""
A tool for listing all EBML schemata in SCHEMA_PATH, including paths in the
EBMLITE_SCHEMA_PATH (if present).
"""

import argparse
import os
import sys

from ebmlite.tools import utils
import ebmlite.util
import ebmlite.core


def main():
    argparser = argparse.ArgumentParser(description=__doc__.strip())

    argparser.add_argument(
        '-o', '--output', metavar="FILE.xml", help="The output file.",
        default=sys.stdout
    )
    argparser.add_argument(
        '-r', '--relative', action="store_true",
        help="Show schema filenames with package-relative path references",
    )
    argparser.add_argument(
        '-p', '--path', nargs='?', action="append",
        help=""
    )

    args = argparser.parse_args()

    paths = []
    for p in args.path:
        paths.extend(p for p in p.split(os.path.pathsep)
                     if p not in ebmlite.core.SCHEMA_PATH)

    ebmlite.util.printSchemata(paths=paths, out=args.output, absolute=not args.relative)


if __name__ == "__main__":
    main()

