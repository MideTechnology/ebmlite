import contextlib
import sys
import os.path

from ebmlite import core


def errPrint(msg):
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()
    exit(1)


def formatArgs(args):
    translator = {
        "input": "filein",
        "output": "fileout",
        "min": "minXml",
    }
    return {translator.get(k, default=k): v for (k, v) in vars(args)}


@contextlib.contextmanager
def load_files(filein, schema, fileout, clobber, binary_output=False):
    if not os.path.exists(filein):
        sys.stderr.write("Input file does not exist: %s\n" % filein)
        exit(1)

    try:
        schema = core.loadSchema(schema)
    except IOError as err:
        errPrint("Error loading schema: %s\n" % err)

    if not fileout:
        yield (schema, sys.stdout)
        return

    fileout = os.path.realpath(os.path.expanduser(fileout))
    if os.path.exists(fileout) and not clobber:
        errPrint("Output file exists: %s" % fileout)
    with open(fileout, ('wb' if binary_output else 'w')) as out:
        yield (schema, out)
