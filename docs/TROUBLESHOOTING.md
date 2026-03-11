"""
EcoFOCIpy Troubleshooting Guide

Solutions to common issues when using EcoFOCIpy

## Installation & Environment Issues

### Problem: ImportError - "No module named 'EcoFOCIpy'"

**Cause:** Package not installed or not in Python path

**Solution:**
```bash
# Install in development mode
pip install -e .

# Or install normally
pip install EcoFOCIpy

# Verify installation
python -c "import EcoFOCIpy; print(EcoFOCIpy.__version__)"
```

### Problem: Version conflicts with dependencies

**Cause:** Incompatible versions of numpy, pandas, or scipy

**Solution:**
```bash
# View current versions
pip list | grep -E "numpy|pandas|scipy"

# Install compatible versions
pip install --upgrade --force-reinstall -r requirements.txt

# Check specific package version
pip show numpy | grep Version
```

### Problem: "ModuleNotFoundError" for submodule

**Cause:** Optional dependencies not installed

**Solution:**
```bash
# Install full dependencies including optional
pip install -e ".[dev]"

# Install specific optional dependencies
pip install xarray netCDF4  # For NetCDF support
```

## Data Loading Issues

### Problem: ParsingError - "Cannot parse file"

**Cause:** 
- File format not recognized
- File corrupted or incomplete
- Wrong parser used

**Solution:**
```python
# Verify file format
with open('file.cnv', 'r') as f:
    header = f.readline()
    print(header)  # Check if valid SBE header

# Use correct parser
from EcoFOCIpy.io import sbe_parser, mtr_parser

# Try explicit parser
try:
    data = sbe_parser.parse_cnv('file.cnv')
except ValueError as e:
    print(f"Parse error: {e}")
    
# Check file encoding
import chardet
with open('file.txt', 'rb') as f:
    result = chardet.detect(f.read())
    print(f"Encoding: {result['encoding']}")
```

### Problem: "Config file not found"

**Cause:** Path incorrect or file doesn't exist

**Solution:**
```python
import os
from pathlib import Path

# Check if file exists
config_path = 'mooring.yaml'
if not os.path.exists(config_path):
    print(f"File not found: {config_path}")
    print(f"Current directory: {os.getcwd()}")
    print("Files in directory:", os.listdir())

# Use absolute path
from pathlib import Path
config_path = Path(__file__).parent / 'config.yaml'

# Or use environment variable
import os
config_dir = os.getenv('ECOFOCI_CONFIG', './')
config_path = os.path.join(config_dir, 'mooring.yaml')
```

### Problem: DataFrame empty or missing data

**Cause:** 
- No data rows in file
- Wrong delimiter
- Headers not recognized

**Solution:**
```python
import pandas as pd

# Check file structure
df = pd.read_csv('file.csv', nrows=5)
print(df.head())
print(df.shape)
print(df.columns)

# Specify delimiter explicitly
df = pd.read_csv('file.csv', delimiter=',', skip_blank_lines=True)

# Check for missing values
print(df.isnull().sum())
```

## Calibration Issues

### Problem: CalibrationError - "Missing coefficients"

**Cause:** Calibration coefficients not found in config

**Solution:**
```python
from EcoFOCIpy.instruments import SBE16

ctd = SBE16(config_file='config.yaml')

# Check if coefficients loaded
print(ctd.calibration_coefficients)

# Verify config file format
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print("Loaded config:", config)

# Required coefficients for SBE16
required = ['g', 'h', 'i', 'j', 'cg', 'ch', 'ci', 'cj']
for coef in required:
    if coef not in config.get('calibration', {}):
        print(f"Missing coefficient: {coef}")
```

### Problem: Calibrated values unrealistic

**Cause:**
- Wrong coefficients
- Wrong calibration equation
- Data unit mismatch

**Solution:**
```python
# Check raw values
print("Raw temp range:", data['temp'].min(), "-", data['temp'].max())
print("Raw cond range:", data['cond'].min(), "-", data['cond'].max())

# Verify calibration coefficients
print("Calibration coefficients used:")
print(ctd.calibration_coefficients)

# Compare with sensor manual
# Example for SBE16: values should be in range:
# Temperature: -2 to 35°C
# Conductivity: 0 to 6 S/m
# Pressure: 0 to sensor_rated depth

# Try manual calibration to debug
from EcoFOCIpy.math.ctd_corrections import practical_salinity

sal = practical_salinity(temp, cond, pressure)
print("Salinity range:", sal.min(), "-", sal.max())
# Should be 0-42 PSU for ocean water
```

## Quality Control Issues

### Problem: "All data flagged as bad"

**Cause:**
- Range thresholds too strict
- Incorrect flag values
- Data scaling issue

**Solution:**
```python
from EcoFOCIpy.qc.ctd_qc import gross_range_test
import numpy as np

# Check data statistics first
print("Data statistics:")
print(f"  Min: {np.nanmin(data)}")
print(f"  Max: {np.nanmax(data)}")
print(f"  Mean: {np.nanmean(data)}")
print(f"  Std: {np.nanstd(data)}")

# Use appropriate ranges
config = {
    'min': -2,      # Realistic minimum
    'max': 35,      # Realistic maximum
}

flags = gross_range_test(data, config)
print("Flag counts:")
print(f"  Good (1): {np.sum(flags == 1)}")
print(f"  Bad (4): {np.sum(flags == 4)}")
print(f"  Missing (9): {np.sum(np.isnan(flags))}")
```

### Problem: Spike detection too aggressive

**Cause:**
- Window too small
- Threshold too low
- Natural variability in data

**Solution:**
```python
from EcoFOCIpy.qc.ctd_qc import spike_test

# Try different thresholds
for threshold in [1.5, 2.0, 2.5, 3.0, 4.0]:
    flags = spike_test(data, {'threshold': threshold, 'window': 5})
    bad_count = np.sum(flags == 4)
    percentage = 100 * bad_count / len(flags)
    print(f"Threshold {threshold}: {bad_count} spikes ({percentage:.1f}%)")

# If too many flagged, increase threshold
# If too few, decrease threshold
```

## Plotting Issues

### Problem: Plots not displaying

**Cause:**
- Non-interactive backend
- Missing matplotlib configuration
- Display server issue (remote)

**Solution:**
```python
import matplotlib.pyplot as plt

# Set interactive backend
plt.switch_backend('TkAgg')  # or 'Qt5Agg', 'MacOSX'

# Or use non-interactive save
fig, ax = plt.subplots()
ax.plot(data)
fig.savefig('output.png', dpi=150, bbox_inches='tight')

# For Jupyter notebooks, add at top:
%matplotlib inline
# or
%matplotlib notebook

# Check which backends are available
import matplotlib
print("Available backends:", matplotlib.backends.backend_registry.list_all())
```

### Problem: Plot colors/styles not working

**Cause:**
- Matplotlib style not applied
- incompatible color map
- Missing font

**Solution:**
```python
import matplotlib.pyplot as plt

# List available styles
print(plt.style.available)

# Use specific style
plt.style.use('seaborn-v0_8-darkgrid')

# Check colormap
import matplotlib.cm as cm
print("Available colormaps:", sorted(cm.colormaps()))

# Update font size
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (10, 6)
```

## Performance Issues

### Problem: "Program running very slowly"

**Cause:**
- Loading entire large files into memory
- Inefficient loops over data
- Plotting large datasets

**Solution:**
```python
# 1. Check memory usage
import psutil
import os
process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")

# 2. Use chunking for large files
chunksize = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunksize):
    process_chunk(chunk)

# 3. Use vectorized operations (not loops)
# Slow:
result = [x * 2 for x in data]
# Fast:
import numpy as np
result = np.array(data) * 2

# 4. Downsample for plotting
# Plot 10000 points instead of 1 million
stride = len(data) // 10000
plt.plot(data[::stride])

# 5. Profile code
import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()
expensive_function()
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### Problem: "Memory error - cannot allocate memory"

**Cause:**
- Loading too much data at once
- Creating unnecessary copies

**Solution:**
```python
import numpy as np

# Use appropriate dtype
# Don't use: data = np.zeros((1000000, 1000), dtype=np.float64)  # ~8GB
# Use: data = np.zeros((1000000, 1000), dtype=np.float32)  # ~4GB

# Read only needed columns
df = pd.read_csv('file.csv', usecols=['time', 'temp', 'sal'])

# Stream processing
import dask.dataframe as dd
df = dd.read_csv('large_file.csv')
result = df.groupby('var').mean().compute()

# Memory mapping for large arrays
mmap_data = np.load('data.npy', mmap_mode='r')
```

## Testing Issues

### Problem: "Tests fail but code works"

**Cause:**
- Test data incorrect
- Environment issue
- Floating point precision

**Solution:**
```python
# Check test data
import numpy as np

# Use np.isclose for float comparison
assert np.isclose(result, expected, rtol=1e-5)
# Not: assert result == expected

# Run single test with verbose output
import pytest
pytest.main(['-v', '-s', 'test_file.py::test_function'])

# Check environment
import sys
print(f"Python: {sys.version}")
import numpy; print(f"NumPy: {numpy.__version__}")

# Review test output
# Look for warnings about missing data
pytest.main(['--tb=short', 'tests/'])
```

### Problem: "ImportError in tests"

**Cause:**
- Package not installed in test environment
- Wrong Python path

**Solution:**
```bash
# Install package in test environment
pip install -e .

# Run tests from package directory
cd /path/to/EcoFOCIpy
python -m pytest tests/

# Check Python path
python -c "import sys; print(sys.path)"
```

## Common "Features" That Are Actually Bugs

### "Data changes after loading"

- **Cause:** View vs. copy in pandas/numpy
- **Solution:**
```python
# Make explicit copy
data_copy = data.copy()

# Check if it's a view
data_view = data[::2]  # Creates view
data_copy = data[::2].copy()  # Creates copy
```

### "Random values in output"

- **Cause:** Uninitialized memory or NaN propagation
- **Solution:**
```python
# Initialize with known values
result = np.zeros_like(data)  # 0.0

# Check for NaN
print(f"NaN count: {np.isnan(data).sum()}")

# Handle NaN appropriately
result = np.nanmean(data)  # Ignores NaN
```

## Getting Help

### When reporting issues, provide:

1. **Minimal reproducible example**
   ```python
   import EcoFOCIpy
   # Minimal code that shows the problem
   ```

2. **Environment information**
   ```bash
   python -c "import EcoFOCIpy; print(EcoFOCIpy.__version__)"
   pip list
   ```

3. **Exact error message and traceback**
   ```
   Traceback (most recent call last):
     ...
     Full traceback here
   ```

4. **Data sample** (if possible, synthetic)

### Resources

- **Documentation:** See `docs/` directory
- **Examples:** See `examples/` directory  
- **Tests:** See `tests/` directory for usage patterns
- **GitHub Issues:** Report bugs with reproducible examples
- **Source Code:** Read function docstrings for implementation details

---

**Last Updated:** 2026-03-10
**Version:** 1.0
"""
