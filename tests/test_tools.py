import filecmp
import os
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

import pytest


SCHEMA_PATH = os.path.join(".", "ebmlite", "schemata", "matroska.xml")


@pytest.mark.script_launch_mode('subprocess')
def test_ebml2xml(script_runner):
    path_base = os.path.join(".", "tests", "video-4{ext}")
    path_in = path_base.format(ext=".ebml")
    path_out = path_base.format(ext=".ebml.xml")
    path_expt = path_base.format(ext=".xml")

    result = script_runner.run(
        "ebml2xml",
        path_in,
        SCHEMA_PATH,
        "--output",
        path_out,
        "--clobber",
    )
    assert result.success

    try:
        root_out = ET.parse(path_out).getroot()
        root_expt = ET.parse(path_expt).getroot()
        # Replace schema location, which varies based on project location on disk
        root_out.set("schemaFile", "./ebmlite/schemata/matroska.xml")
        root_out.set("source", "./" + str(PurePosixPath(Path(root_out.attrib["source"]))))

        # Output file is not in canonical form (see Py3.8+: ET.canonicalize)
        # -> compare key properties of each element
        def assert_elements_are_equiv(e1, e2):
            assert e1.tag == e2.tag and e1.attrib == e2.attrib

        assert_elements_are_equiv(root_out, root_expt)
        for e_out, e_expt in zip(root_out.iter(), root_expt.iter()):
            assert_elements_are_equiv(e_out, e_expt)

    finally:
        # Remove the output file in all cases
        try:
            os.remove(path_out)
        except FileNotFoundError:
            pass


@pytest.mark.script_launch_mode('subprocess')
def test_xml2ebml(script_runner):
    path_base = os.path.join(".", "tests", "video-4{ext}")
    path_in = path_base.format(ext=".xml")
    path_out = path_base.format(ext=".xml.ebml")
    path_expt = path_base.format(ext=".ebml")

    result = script_runner.run(
        "xml2ebml",
        path_in,
        SCHEMA_PATH,
        "--output",
        path_out,
        "--clobber",
    )
    assert result.success

    try:
        assert filecmp.cmp(path_out, path_expt, shallow=False)

    finally:
        # Remove the output file in all cases
        try:
            os.remove(path_out)
        except FileNotFoundError:
            pass


@pytest.mark.script_launch_mode('subprocess')
def test_view(script_runner):
    path_base = os.path.join(".", "tests", "video-4{ext}")
    path_in = path_base.format(ext=".ebml")
    path_out = path_base.format(ext=".xml.txt")
    path_expt = path_base.format(ext=".txt")

    result = script_runner.run(
        "view-ebml",
        path_in,
        SCHEMA_PATH,
        "--output",
        path_out,
        "--clobber",
    )
    assert result.success

    try:
        assert filecmp.cmp(path_out, path_expt, shallow=False)

    finally:
        # Remove the output file in all cases
        try:
            os.remove(path_out)
        except FileNotFoundError:
            pass
