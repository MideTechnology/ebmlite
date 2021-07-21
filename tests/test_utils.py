import os
import filecmp

import pytest


SCHEMA_PATH = os.path.join(".", "ebmlite", "schemata", "matroska.xml")

@pytest.mark.script_launch_mode('subprocess')
def test_ebml2xml(script_runner):
    path_base = os.path.join(".", "tests", "video-1{ext}")
    path_in = path_base.format(ext=".mkv")
    path_out = path_base.format(ext=".mkv.xml")
    path_expt = path_base.format(ext=".xml")

    result = script_runner.run(
        "python", "-m", "ebmlite.util", "ebml2xml",
        path_in,
        SCHEMA_PATH,
        "--output=" + path_out,
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
def test_xml2ebml(script_runner):
    path_base = os.path.join(".", "tests", "video-1{ext}")
    path_in = path_base.format(ext=".xml")
    path_out = path_base.format(ext=".xml.ebml")
    path_expt = path_base.format(ext=".mkv")

    result = script_runner.run(
        "python", "-m", "ebmlite.util", "xml2ebml",
        path_in,
        SCHEMA_PATH,
        "--output=" + path_out,
    )
    assert result.success

    try:
        assert filecmp.cmp(path_out, path_expt, shallow=False)

    finally:
        # Remove the output file in all cases
        try:
            pass
            os.remove(path_out)
        except FileNotFoundError:
            pass
