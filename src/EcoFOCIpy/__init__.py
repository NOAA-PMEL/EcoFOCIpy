"""
EcoFOCIpy: Python Tools for Oceanographic Data Processing.

A comprehensive Python package for processing and analyzing oceanographic data
collected by NOAA's EcoFOCI (Ecosystems and Fisheries-Oceanography Coordinated
Investigations) program.

This package provides tools and utilities for working with various oceanographic
instruments including:
- CTD (Conductivity-Temperature-Depth) profilers
- Moored sensor arrays
- ADCP (Acoustic Doppler Current Profiler)
- Nutrient sensors (SUNA, ISUS)
- Optical sensors (WET Labs)
- Temperature/conductivity loggers

Main modules:

    - ``io``: File I/O operations (NetCDF, CSV, etc.)
    - ``math``: Oceanographic calculations and transformations
    - ``qc``: Quality control and data flagging
    - ``plots``: Visualization tools
    - ``epic``: EPIC (Oceanographic Data Interchange Format) utilities

Example usage:

    >>> import EcoFOCIpy
    >>> from EcoFOCIpy import epic, io, math, plots, qc

Version: 0.2.6
Author: NOAA/PMEL EcoFOCI Team
License: BSD-3-Clause
Repository: https://github.com/NOAA-PMEL/EcoFOCIpy
Documentation: https://github.com/NOAA-PMEL/EcoFOCIpy/wiki
"""

__version__ = "0.2.6"
__author__ = "NOAA/PMEL EcoFOCI Team"
__license__ = "BSD-3-Clause"
__all__ = [
    "io",
    "math",
    "qc",
    "plots",
    "epic",
]

try:
    from . import epic  # noqa: F401
    from . import io  # noqa: F401
    from . import math  # noqa: F401
    from . import plots  # noqa: F401
    from . import qc  # noqa: F401
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import all EcoFOCIpy submodules: {e}")
