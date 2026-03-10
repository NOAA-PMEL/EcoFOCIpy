"""
EcoFOCIpy Documentation Index

Complete guide to all EcoFOCIpy documentation resources.

## Quick Navigation

### For Different Needs

**I want to...**

- **Get started quickly** → See [Getting Started](#getting-started)
- **Learn by example** → See [Examples & Notebooks](#examples--notebooks)
- **Look up a function** → See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- **Understand a module deeply** → See [MODULE_REFERENCE.md](MODULE_REFERENCE.md)
- **Fix a problem** → See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Write tests** → See [../tests/TESTING_GUIDE.md](../tests/TESTING_GUIDE.md)
- **Contribute code** → See [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **See what's changed** → See [../HISTORY.rst](../HISTORY.rst)

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/NOAA-PMEL/EcoFOCIpy.git
cd EcoFOCIpy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### First Steps

```python
# 1. Load a data file
from EcoFOCIpy.instruments import SBE16

ctd = SBE16(config_file='your_config.yaml')
data = ctd.load_data('your_data.cnv')

# 2. Apply quality control
from EcoFOCIpy.qc.ctd_qc import apply_all_checks

flags = apply_all_checks(data)

# 3. Export results
ctd.to_netcdf('output.nc', data=data)

# 4. Create visualization
from EcoFOCIpy.plots import sbe_ctd_plots

fig, axes = sbe_ctd_plots.profile_plots(data)
```

## Documentation Files

### Core Documentation

| File | Purpose | Best For |
|------|---------|----------|
| [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) | Quick lookup of common functions | Looking up API quickly |
| [MODULE_REFERENCE.md](MODULE_REFERENCE.md) | Complete module documentation | Understanding modules deeply |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Solutions to common problems | Fixing errors |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Guidelines for contributing | Contributing to EcoFOCIpy |
| [../tests/TESTING_GUIDE.md](../tests/TESTING_GUIDE.md) | Testing instructions | Writing and running tests |

### Source Documentation

| File | Purpose |
|------|---------|
| [../README.md](../README.md) | Project overview |
| [../HISTORY.rst](../HISTORY.rst) | Release history and changelog |
| [../CREDITS.md](../CREDITS.md) | Authors and contributors |
| [../LICENSE.md](../LICENSE.md) | License information |

## By Module

### instruments - Data Parsers & Processors

**Quick Start:**
```python
from EcoFOCIpy.instruments import SBE16, SUNA, ADCP

ctd = SBE16(config_file='config.yaml')
data = ctd.load_data('data.cnv')
```

**See Also:**
- [API_QUICK_REFERENCE.md - instruments](API_QUICK_REFERENCE.md#instruments-module---quick-reference)
- [MODULE_REFERENCE.md - instruments](MODULE_REFERENCE.md#instruments-module)

### io - File I/O

**Quick Start:**
```python
from EcoFOCIpy.io import sbe_parser, ncCFsave
import xarray as xr

data = sbe_parser.parse_cnv('file.cnv')
ds = xr.Dataset({'temp': (['time'], data)})
ds.to_netcdf('output.nc')
```

**See Also:**
- [API_QUICK_REFERENCE.md - io](API_QUICK_REFERENCE.md#io-module---quick-reference)
- [MODULE_REFERENCE.md - io](MODULE_REFERENCE.md#io-module)

### math - Oceanographic Calculations

**Quick Start:**
```python
from EcoFOCIpy.math.ctd_corrections import practical_salinity

salinity = practical_salinity(temperature, conductivity, pressure)
```

**See Also:**
- [API_QUICK_REFERENCE.md - math](API_QUICK_REFERENCE.md#math-module---quick-reference)
- [MODULE_REFERENCE.md - math](MODULE_REFERENCE.md#math-module)

### qc - Quality Control

**Quick Start:**
```python
from EcoFOCIpy.qc.ctd_qc import apply_all_checks

flags = apply_all_checks(data, ranges={'temp': (-2, 30)})
good_data = data[flags.min(axis=1) <= 2]
```

**See Also:**
- [API_QUICK_REFERENCE.md - qc](API_QUICK_REFERENCE.md#qc-module---quick-reference)
- [MODULE_REFERENCE.md - qc](MODULE_REFERENCE.md#qc-module)

### plots - Visualization

**Quick Start:**
```python
from EcoFOCIpy.plots import sbe_ctd_plots

fig, axes = sbe_ctd_plots.profile_plots(data)
fig = sbe_ctd_plots.ts_diagram(temperature, salinity, pressure)
```

**See Also:**
- [API_QUICK_REFERENCE.md - plots](API_QUICK_REFERENCE.md#plots-module---quick-reference)
- [MODULE_REFERENCE.md - plots](MODULE_REFERENCE.md#plots-module)

### epic - EPIC Format

**Quick Start:**
```python
from EcoFOCIpy.epic.EPIC_timeconvert import EPICTIMESTAMP

epic_time = EPICTIMESTAMP.datetime_to_epic(dt_list)
```

**See Also:**
- [API_QUICK_REFERENCE.md - epic](API_QUICK_REFERENCE.md#epic-module---quick-reference)
- [MODULE_REFERENCE.md - epic](MODULE_REFERENCE.md#epic-module)

## Examples & Notebooks

### Example Scripts

Located in `examples/` directory:

- `load_sbe16_data.py` - Load and display SBE16 CTD data
- `apply_quality_control.py` - Apply QC checks to dataset
- `compare_sensors.py` - Compare multiple sensor readings
- And many more...

**To run examples:**
```bash
cd examples/
python load_sbe16_data.py
```

### Jupyter Notebooks

Located in `notebooks/` directory:

- `01_Getting_Started.ipynb` - Introduction to EcoFOCIpy
- `02_Data_Loading.ipynb` - Loading various data formats
- `03_Quality_Control.ipynb` - Applying QC procedures
- `04_Calibration.ipynb` - Instrument calibration
- `05_Analysis_and_Plotting.ipynb` - Data analysis and visualization
- And more...

**To run notebooks:**
```bash
jupyter notebook notebooks/
```

## Common Workflows

### Workflow 1: Load and Calibrate CTD Data

```python
from EcoFOCIpy.instruments import SBE16

# Initialize instrument
ctd = SBE16(config_file='config.yaml')

# Load raw data
raw_data = ctd.load_data('raw_data.cnv')

# Apply calibration
calibrated_data = ctd.calibrate(raw_data)

# Save to NetCDF
ctd.to_netcdf('output.nc', data=calibrated_data)
```

**See Also:**
- [MODULE_REFERENCE.md - Configuration Files](MODULE_REFERENCE.md#configuration-files)
- [TROUBLESHOOTING.md - Calibration Issues](TROUBLESHOOTING.md#calibration-issues)

### Workflow 2: Apply Quality Control

```python
from EcoFOCIpy.qc.ctd_qc import apply_all_checks
import pandas as pd

# Load data
data = pd.read_csv('data.csv', index_col='time', parse_dates=True)

# Apply QC procedures
flags = apply_all_checks(
    data,
    ranges={'temperature': (-2, 30), 'salinity': (0, 40)},
    spike_threshold=3.0,
    rate_threshold=5.0
)

# Filter and keep good data
good_data = data[flags.min(axis=1) <= 2]
good_data.to_csv('qc_data.csv')
```

**See Also:**
- [TROUBLESHOOTING.md - Quality Control Issues](TROUBLESHOOTING.md#quality-control-issues)
- [../tests/TESTING_GUIDE.md](../tests/TESTING_GUIDE.md)

### Workflow 3: Oceanographic Calculations

```python
from EcoFOCIpy.math import ctd_corrections, lanzcos

# Calculate properties from T, C, P
salinity = ctd_corrections.practical_salinity(temp, cond, pres)
sigma_t = ctd_corrections.potential_density(temp, salinity, pres)

# Apply filtering
filtered_temp = lanzcos.lanczos_filter(temperature, window=24, data_freq=1)
```

**See Also:**
- [API_QUICK_REFERENCE.md - math](API_QUICK_REFERENCE.md#math-module---quick-reference)

### Workflow 4: Visualization

```python
from EcoFOCIpy.plots import sbe_ctd_plots
import matplotlib.pyplot as plt

# Load and process data
ctd = SBE16(config_file='config.yaml')
data = ctd.load_data('data.cnv')
calibrated = ctd.calibrate(data)

# Create publication-quality plots
fig, axes = sbe_ctd_plots.profile_plots(calibrated, figname='profiles.png')
fig2 = sbe_ctd_plots.ts_diagram(calibrated['temp'], calibrated['sal'], calibrated['pres'])

plt.show()
```

**See Also:**
- [TROUBLESHOOTING.md - Plotting Issues](TROUBLESHOOTING.md#plotting-issues)

## Common Errors

### Error: "No module named 'EcoFOCIpy'"

**See:** [TROUBLESHOOTING.md - Installation & Environment Issues](TROUBLESHOOTING.md#problem-importerror---no-module-named-ecofocipy)

### Error: "Cannot parse file"

**See:** [TROUBLESHOOTING.md - Data Loading Issues](TROUBLESHOOTING.md#problem-parsingerror---cannot-parse-file)

### Error: "Missing calibration coefficients"

**See:** [TROUBLESHOOTING.md - Calibration Issues](TROUBLESHOOTING.md#problem-calibrationerror---missing-coefficients)

### Error: "All data flagged as bad"

**See:** [TROUBLESHOOTING.md - Quality Control Issues](TROUBLESHOOTING.md#problem-all-data-flagged-as-bad)

## Type Hints

EcoFOCIpy uses Python type hints throughout. Common type signatures:

```python
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

# Common pattern: accept multiple input types
def process_data(
    data: Union[np.ndarray, pd.Series],
    config: Optional[Dict[str, float]] = None
) -> Tuple[np.ndarray, Dict[str, float]]:
    """Process oceanographic measurements."""
    pass
```

**See Also:**
- [CONTRIBUTING.md - Type Hints](../CONTRIBUTING.md#type-hints)
- [MODULE_REFERENCE.md - Type Hints Reference](MODULE_REFERENCE.md#type-hints-reference)

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_qc.py

# Run specific test
pytest tests/test_qc.py::TestRangeCheck::test_all_good_data

# Run with coverage
pytest --cov=EcoFOCIpy --cov-report=html
```

**See Also:**
- [../tests/TESTING_GUIDE.md](../tests/TESTING_GUIDE.md)
- [../CONTRIBUTING.md](../CONTRIBUTING.md)

## Contributing

### To Contribute:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and write tests
4. Run tests: `pytest`
5. Commit: `git commit -m "feat: add my feature"`
6. Push and create pull request

**See Also:**
- [../CONTRIBUTING.md](../CONTRIBUTING.md)
- [../tests/TESTING_GUIDE.md](../tests/TESTING_GUIDE.md)

## Resources

### External Documentation

- **NumPy Documentation:** https://numpy.org/doc/
- **Pandas Documentation:** https://pandas.pydata.org/docs/
- **XArray Documentation:** https://xarray.pydata.org/
- **Matplotlib Documentation:** https://matplotlib.org/
- **NetCDF4 Python Docs:** https://unidata.github.io/netcdf4-python/

### Related Projects

- **EcoFOCIpy Repository:** https://github.com/NOAA-PMEL/EcoFOCIpy
- **EcoFOCI Program:** https://www.pmel.noaa.gov/ecofoci/
- **NOAA PMEL:** https://www.pmel.noaa.gov/

## Version Information

- **Latest Version:** 0.2.5
- **Release Date:** February 18, 2026
- **Python Version:** 3.8+

**See Also:**
- [../HISTORY.rst](../HISTORY.rst)
- [../CITATION.cff](../CITATION.cff)

## Document Organization

```
docs/
├── INDEX.md (this file)                     # Documentation index and guide
├── README.md                                 # Main README
├── MODULE_REFERENCE.md                      # Complete API documentation
├── API_QUICK_REFERENCE.md                   # Quick lookup guide
├── TROUBLESHOOTING.md                       # Solutions to common problems
├── CONTRIBUTING.md                          # Contribution guidelines
└── tests/
    └── TESTING_GUIDE.md                     # Testing documentation
```

## Quick Reference Tables

### QC Flags

| Flag | Meaning | Notes |
|------|---------|-------|
| 1 | Good data | Data passes all QC tests |
| 2 | Questionable/suspect | Marginal but usable |
| 3 | Bad data | Should not be used |
| 4 | Out of range | Outside expected range |
| 5 | Missing value | No measurement |
| 9 | No QC performed | Not evaluated |

### Common Python Imports

```python
# Standard sci-py stack
import numpy as np
import pandas as pd
import scipy as sp

# EcoFOCIpy main modules
from EcoFOCIpy import instruments, io, math, qc, plots, epic

# Specific instruments
from EcoFOCIpy.instruments import SBE16, SBE37, SUNA, ISUS, ADCP

# File I/O
from EcoFOCIpy.io import sbe_parser, ncCFsave
import xarray as xr

# Quality control
from EcoFOCIpy.qc.ctd_qc import (
    gross_range_test,
    spike_test,
    rate_of_change_test,
    apply_all_checks
)

# Plotting
from EcoFOCIpy.plots import sbe_ctd_plots
```

## Support & Feedback

### Getting Help

1. **Check Documentation** - See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) for quick answers
2. **Search Troubleshooting** - See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. **Review Examples** - See `examples/` and `notebooks/` directories
4. **Read Source Code** - Docstrings contain detailed information
5. **Check Tests** - Tests demonstrate proper usage

### Report Issues

- GitHub Issues: https://github.com/NOAA-PMEL/EcoFOCIpy/issues
- Include: error message, minimal reproducible example, environment info

---

**Last Updated:** 2026-03-10
**Documentation Version:** 2.0
**EcoFOCIpy Version:** 0.2.5
"""
