# Copyright (c) 2021 EcoFOCIpy
"""Setup script for installing EcoFOCIpy."""

import sys

from setuptools import setup

if sys.version_info[0] < 3:
    error = """
    EcoFOCIpy requires the Python 3.8 or above, but will install on
    all versions of python3.

    Python {py} detected.
    """.format(py='.'.join([str(v) for v in sys.version_info[:3]]))

    print(error)  # noqa: T001
    sys.exit(1)

setup()
