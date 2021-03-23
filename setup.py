# Copyright (c) 2021 EcoFOCI Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
"""Setup script for installing EcoFOCIpy."""

import sys

from setuptools import setup

if sys.version_info[0] < 3:
    error = """
    EcoFOCIpy requires the Python 3.6 or above (tested on 3.8+).
    If you're using Python 2.7.

    Python {py} detected.
    """.format(py='.'.join([str(v) for v in sys.version_info[:3]]))

    print(error)  # noqa: T001
    sys.exit(1)

setup(use_scm_version={'version_scheme': 'post-release'})
