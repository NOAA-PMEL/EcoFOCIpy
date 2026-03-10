"""
EcoFOCIpy Module Reference

Complete API documentation for EcoFOCIpy modules with type hints and examples.

## Module Overview

EcoFOCIpy is organized into several main modules:

### Core Modules

- **instruments**: Device-specific data parsers and processors
- **io**: File I/O operations (NetCDF, CSV, YAML, etc.)
- **math**: Oceanographic calculations and transformations
- **qc**: Quality control and data flagging
- **plots**: Visualization and plotting utilities
- **epic**: EPIC format utilities

## instruments Module

### SBE Temperature/Conductivity Devices

#### SBE16 (moored CTD)
```python
from EcoFOCIpy.instruments import SBE16

ctd = SBE16(config_file='mooring.yaml')
data = ctd.load_data('raw_data.cnv')
calibrated = ctd.calibrate(data)
ctd.to_netcdf('output.nc', data=calibrated)
```

#### SBE37 (Temperature/Conductivity Logger)
```python
from EcoFOCIpy.instruments import SBE37

logger = SBE37(config=config_dict)
data = logger.load_data('sbe37_raw.hex')
```

#### SBE39 (Temperature Logger)
```python
from EcoFOCIpy.instruments import SBE39

temp_logger = SBE39(config=config_dict)
data = temp_logger.load_data('sbe39_raw.hex')
```

#### SBE56 (Temperature Logger)
```python
from EcoFOCIpy.instruments import SBE56

logger = SBE56()
data = logger.load_data('sbe56_file.hex')
```

### Nutrient Sensors

#### SUNA (Submersible UV Nitrate Analyzer)
```python
from EcoFOCIpy.instruments import SUNA

suna = SUNA(config=config_dict)
data = suna.load_data('suna_raw.txt')
processed = suna.process(data)
```

#### ISUS (In Situ Ultraviolet Spectrophotometer)
```python
from EcoFOCIpy.instruments import ISUS

isus = ISUS(config=config_dict)
data = isus.load_data('isus_raw.txt')
```

### Current Profilers

#### ADCP (Acoustic Doppler Current Profiler)
```python
from EcoFOCIpy.instruments import ADCP

adcp = ADCP(config=config_dict)
data = adcp.load_data('adcp_raw.000')
u, v = adcp.rotate_velocities(data)
```

### Other Sensors

#### WET Labs Optical Sensors
```python
from EcoFOCIpy.instruments.wetlabs_parser import WetLabs

wetlabs = WetLabs(channels=3)  # 1, 2, or 3 channel sensor
data = wetlabs.load_data('wetlabs_raw.txt')
```

## io Module

### NetCDF File Operations

```python
from EcoFOCIpy.io import ncCFsave

# Save data to CF-compliant NetCDF
ncCFsave.save_to_netcdf(
    filename='output.nc',
    data=data_dict,
    metadata=metadata_dict,
    dims={'time': 100, 'depth': 50}
)

# Load NetCDF file
import xarray as xr
ds = xr.open_dataset('output.nc')
```

### Parser Functions

```python
from EcoFOCIpy.io import sbe_parser, mtr_parser

# Parse SBE CNV files
data = sbe_parser.parse_cnv('file.cnv')

# Parse MTR files
data = mtr_parser.parse_mtr('file.hex')

# Parse WPAK files
from EcoFOCIpy.io import wpak_parser
data = wpak_parser.parse_wpak('file.dat')
```

### ERDDAP Data Retrieval

```python
from EcoFOCIpy.io.erddap import ErddapClient

client = ErddapClient(base_url='https://erddap.example.com')
df = client.search_datasets('mooring')
data = client.get_dataset(dataset_id='ID')
```

## math Module

### Oceanographic Calculations

#### CTD Calibrations
```python
from EcoFOCIpy.math import ctd_corrections

# Calculate salinity from T and C
salinity = ctd_corrections.practical_salinity(
    temp_insitu=temperature,
    cond_insitu=conductivity,
    pressure=pressure
)

# Calculate derived properties
sigma = ctd_corrections.potential_density(
    temp_insitu=temperature,
    salinity=salinity,
    pressure=pressure
)
```

#### Oxygen Corrections
```python
from EcoFOCIpy.math.oxygen_corr import AndersonOxygenCorrection

oxy_corr = AndersonOxygenCorrection()
corrected_oxy = oxy_corr.apply(
    oxygen=oxygen_raw,
    temp=temperature,
    sal=salinity
)
```

#### Nitrate Corrections
```python
from EcoFOCIpy.math.nitrates_corr import SUNACorrection

suna_corr = SUNACorrection()
nitrate_corrected = suna_corr.apply(
    counts=counts,
    temp_sensor=temp,
    salinity_sensor=sal
)
```

#### Filtering
```python
from EcoFOCIpy.math import lanzcos, cleaning

# Apply low-pass Lanczos filter
filtered = lanzcos.lanczos_filter(
    data=time_series,
    window=24,  # hours
    data_freq=1  # samples per hour
)

# Despiking
despike = cleaning.despike(
    data=time_series,
    threshold=3.0  # standard deviations
)
```

#### Geographic Tools
```python
from EcoFOCIpy.math.geotools import haversine

# Calculate distance between two points
distance_m = haversine.haversine(
    lat1=57.0, lon1=179.5,
    lat2=57.1, lon2=179.6
)
```

## qc Module

### Quality Control Functions

```python
from EcoFOCIpy.qc.ctd_qc import (
    gross_range_test,
    spike_test,
    stuck_value_test
)

# Range check
flags = gross_range_test(
    data=temperature,
    config={'min': -2, 'max': 30}
)

# Spike detection
flags = spike_test(
    data=temperature,
    config={'window': 5, 'threshold': 2.0}
)

# Stuck value detection
flags = stuck_value_test(
    data=temperature,
    config={'consecutive_limit': 10}
)
```

## plots Module

### Visualization Functions

#### CTD Profile Plots
```python
from EcoFOCIpy.plots import sbe_ctd_plots

fig, axes = sbe_ctd_plots.profile_plots(
    data_dict=processed_ctd_data,
    figname='ctd_profiles.png'
)

fig = sbe_ctd_plots.ts_diagram(
    temperature=temp,
    salinity=sal,
    pressure=pres
)
```

#### Time Series Plots
```python
from EcoFOCIpy.plots import TimeSeriesStickPlot

stick_plot = TimeSeriesStickPlot.StickPlot(
    time=times,
    velocity_east=u,
    velocity_north=v
)
stick_plot.plot()
```

## epic Module

### EPIC Format Tools

```python
from EcoFOCIpy.epic.EPIC_timeconvert import EPICTIMESTAMP

# Convert time formats
epic_time = EPICTIMESTAMP.datetime_to_epic(
    dt_list=datetime_list
)

dt_list = EPICTIMESTAMP.epic_to_datetime(
    epic_time_tuple
)
```

## Configuration Files

### YAML Mooring Configuration

```yaml
mooring_number: M1
latitude: 57.0
longitude: -179.5
water_depth: 1000
deployment_date: 2024-01-15
recovery_date: 2024-06-30

instruments:
  - type: SBE16
    serial_number: 12345
    depth: 100
    calibration:
      temp_coefficients: [...]
      cond_coefficients: [...]
      
  - type: SBE37
    serial_number: 67890
    depth: 500
```

## Type Hints Reference

Common type hints used throughout EcoFOCIpy:

```python
from typing import (
    Dict, List, Optional, Tuple, Union
)
import numpy as np
import pandas as pd

# Common type aliases
DataArray = Union[np.ndarray, list]
DataSeries = Union[pd.Series, np.ndarray]
DataTable = Union[pd.DataFrame, np.ndarray]
Numeric = Union[int, float, np.number]

# Example function signature
def process_data(
    data: DataSeries,
    method: str = 'default',
    params: Optional[Dict[str, float]] = None,
) -> Tuple[DataArray, Dict[str, float]]:
    '''Process oceanographic measurements.'''
    pass
```

## Error Handling

```python
from EcoFOCIpy.exceptions import (
    ParsingError,
    CalibrationError,
    ConfigurationError,
)

try:
    data = instrument.load_data(filename)
except ParsingError as e:
    print(f"Failed to parse file: {e}")
except CalibrationError as e:
    print(f"Calibration issue: {e}")
```

## Logging

```python
import logging

# Enable debug logging
logging.getLogger('EcoFOCIpy').setLevel(logging.DEBUG)

# Create logger for your code
logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.debug(f"Data shape: {data.shape}")
logger.warning("Missing calibration coefficient")
logger.error("Failed to process file")
```

## Performance Tips

1. **Use vectorized operations** (NumPy, Pandas)
2. **Avoid loops over large arrays**
3. **Use data type appropriate sizes** (float32 vs float64)
4. **Cache computed values**
5. **Profile code with `cProfile`**

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = expensive_function(large_data)

profiler.disable()
stats = pstats.Stats(profiler)
stats.print_stats()
```

## Common Recipes

### Load and Process Mooring Data

```python
from EcoFOCIpy import instruments, io

# Load configuration
config = io.load_yaml('mooring.yaml')

# Initialize instrument
ctd = instruments.SBE16(config=config)

# Load and process data
raw_data = ctd.load_data('sbe16_raw.cnv')
calibrated = ctd.calibrate(raw_data)

# Export to NetCDF
ctd.to_netcdf('output.nc', data=calibrated)
```

### Apply Quality Control

```python
from EcoFOCIpy.qc import ctd_qc
import pandas as pd

# Load data
data = pd.read_csv('data.csv', index_col='time', parse_dates=True)

# Apply QC
flags = ctd_qc.apply_all_checks(
    data,
    ranges={'temperature': (-2, 30), 'salinity': (0, 40)},
    spike_threshold=3.0
)

# Filter good data
good_data = data[flags.min(axis=1) <= 2]
```

---

For more examples, see the `examples/` and `notebooks/` directories.

Last Updated: 2026-03-10
