"""
EcoFOCIpy Quick API Reference

Quick lookup guide for common EcoFOCIpy functions and classes.
For detailed documentation, see MODULE_REFERENCE.md

## Quick Import Guide

```python
# Core imports
from EcoFOCIpy import instruments, io, math, qc, plots, epic
from EcoFOCIpy.instruments import SBE16, SBE37, SUNA, ISUS, ADCP
from EcoFOCIpy.io import ncCFsave, sbe_parser, mtr_parser
from EcoFOCIpy.math import ctd_corrections, lanzcos, cleaning
from EcoFOCIpy.qc import ctd_qc
from EcoFOCIpy.plots import sbe_ctd_plots
```

## instruments Module - Quick Reference

### SBE16 CTD
```python
ctd = SBE16(config_file='config.yaml')
data = ctd.load_data('file.cnv')
data = ctd.calibrate(data)
ctd.to_netcdf(filename, data=data)
```

### SBE37/SBE39/SBE56 Temperature Loggers
```python
logger = SBE37(config=config_dict)  # or SBE39(), SBE56()
data = logger.load_data('file.hex')
```

### SUNA Nitrate Sensor
```python
suna = SUNA(config=config_dict)
data = suna.load_data('file.txt')
processed = suna.process(data)
```

### ISUS Nitrate Sensor
```python
isus = ISUS(config=config_dict)
data = isus.load_data('file.txt')
```

### ADCP Current Profiler
```python
adcp = ADCP(config=config_dict)
data = adcp.load_data('file.000')
u, v = adcp.rotate_velocities(data)
```

## io Module - Quick Reference

### Load/Save NetCDF
```python
import xarray as xr

# Save to NetCDF
xr.Dataset(data_vars).to_netcdf('output.nc')

# Load from NetCDF
ds = xr.open_dataset('input.nc')
data = ds.to_array().values
```

### Parse Raw Files
```python
from EcoFOCIpy.io import sbe_parser, mtr_parser, wpak_parser

sbe_data = sbe_parser.parse_cnv('file.cnv')
mtr_data = mtr_parser.parse_mtr('file.hex')
wpak_data = wpak_parser.parse_wpak('file.dat')
```

### Configuration Files
```python
from EcoFOCIpy.io import load_yaml, save_yaml

config = load_yaml('config.yaml')
save_yaml('new_config.yaml', config)
```

## math Module - Quick Reference

### Practical Salinity from T and C
```python
from EcoFOCIpy.math.ctd_corrections import practical_salinity

sal = practical_salinity(temp_insitu, cond_insitu, pressure)
```

### Potential Density (Sigma)
```python
from EcoFOCIpy.math.ctd_corrections import potential_density

sigma = potential_density(temp_insitu, salinity, pressure)
```

### Oxygen Corrections
```python
from EcoFOCIpy.math.oxygen_corr import AndersonOxygenCorrection

oxy_corr = AndersonOxygenCorrection()
oxy_corrected = oxy_corr.apply(oxygen=oxy_raw, temp=temp, sal=sal)
```

### Nitrate Corrections (SUNA)
```python
from EcoFOCIpy.math.nitrates_corr import SUNACorrection

suna_corr = SUNACorrection()
no3 = suna_corr.apply(counts=counts, temp_sensor=temp, salinity=sal)
```

### Low-pass Filtering (Lanczos)
```python
from EcoFOCIpy.math.lanzcos import lanczos_filter

filtered = lanczos_filter(data, window=24, data_freq=1)
```

### Despiking
```python
from EcoFOCIpy.math.cleaning import despike

clean = despike(data, threshold=3.0)
```

### Distance Calculation (Haversine)
```python
from EcoFOCIpy.math.geotools import haversine

distance_m = haversine(57.0, 179.5, 57.1, 179.6)
```

## qc Module - Quick Reference

### Range Check (Gross Error)
```python
from EcoFOCIpy.qc.ctd_qc import gross_range_test

flags = gross_range_test(temperature, config={'min': -2, 'max': 30})
```

### Spike Test
```python
from EcoFOCIpy.qc.ctd_qc import spike_test

flags = spike_test(temperature, config={'window': 5, 'threshold': 2.0})
```

### Stuck Value Test
```python
from EcoFOCIpy.qc.ctd_qc import stuck_value_test

flags = stuck_value_test(temperature, config={'consecutive_limit': 10})
```

### Rate of Change Test
```python
from EcoFOCIpy.qc.ctd_qc import rate_of_change_test

flags = rate_of_change_test(temperature, config={'threshold': 5.0})
```

### Apply All QC Checks
```python
from EcoFOCIpy.qc.ctd_qc import apply_all_checks

flags = apply_all_checks(data, ranges, spike_threshold=3.0, rate_threshold=5.0)
```

## plots Module - Quick Reference

### CTD Profile Plots
```python
from EcoFOCIpy.plots import sbe_ctd_plots

fig, axes = sbe_ctd_plots.profile_plots(data_dict, figname='profiles.png')
```

### T-S Diagram
```python
from EcoFOCIpy.plots import sbe_ctd_plots

fig = sbe_ctd_plots.ts_diagram(temperature, salinity, pressure)
```

### Stick Plots (Current)
```python
from EcoFOCIpy.plots.TimeSeriesStickPlot import StickPlot

stick = StickPlot(time, u, v)
stick.plot()
```

## epic Module - Quick Reference

### Time Format Conversions
```python
from EcoFOCIpy.epic.EPIC_timeconvert import EPICTIMESTAMP

# Datetime to EPIC
epic_time = EPICTIMESTAMP.datetime_to_epic(dt_list)

# EPIC to Datetime
dt_list = EPICTIMESTAMP.epic_to_datetime(epic_time_tuple)
```

## Common Workflows

### Workflow 1: Load CTD, Calibrate, Save
```python
from EcoFOCIpy.instruments import SBE16

ctd = SBE16(config_file='mooring.yaml')
raw = ctd.load_data('raw.cnv')
cal = ctd.calibrate(raw)
ctd.to_netcdf('output.nc', data=cal)
```

### Workflow 2: Apply Quality Control
```python
from EcoFOCIpy.qc.ctd_qc import apply_all_checks
import pandas as pd

data = pd.read_csv('data.csv')
flags = apply_all_checks(data, ranges={'temp': (-2, 30), 'sal': (0, 40)})
good = data[flags.min(axis=1) <= 2]
```

### Workflow 3: Filter Time Series
```python
from EcoFOCIpy.math.lanzcos import lanczos_filter

filtered = lanczos_filter(time_series, window=24, data_freq=1)
```

### Workflow 4: Convert Salinity from T and C
```python
from EcoFOCIpy.math.ctd_corrections import practical_salinity

salinity = practical_salinity(temperature, conductivity, pressure)
```

## Type Hints Used

| Type | Usage |
|------|-------|
| `np.ndarray` | NumPy arrays |
| `pd.Series` | Pandas Series |
| `pd.DataFrame` | Pandas DataFrames |
| `Dict[str, float]` | Configuration dictionaries |
| `List[float]` | Lists of numbers |
| `Optional[X]` | Can be X or None |
| `Union[X, Y]` | Can be X or Y |
| `Tuple[X, Y]` | Tuple of X and Y |

## Configuration Format (YAML)

```yaml
mooring:
  number: M1
  latitude: 57.0
  longitude: -179.5
  
instruments:
  - type: SBE16
    serial: 12345
    depth: 100
    calibration:
      temp: [...]
      cond: [...]
```

## QC Flags

| Flag | Meaning |
|------|---------|
| 1 | Good data |
| 2 | Questionable/suspect |
| 3 | Bad data |
| 4 | Out of range |
| 5 | Missing value |
| 9 | No QC performed |

## Error Types

```python
from EcoFOCIpy.exceptions import (
    ParsingError,        # File parsing failed
    CalibrationError,    # Calibration coefficient issue
    ConfigurationError,  # Invalid configuration
)
```

## Debug Logging

```python
import logging

# Enable debug output
logging.getLogger('EcoFOCIpy').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug(f"Data shape: {data.shape}")
logger.warning("Missing coefficient")
logger.error("Failed to process")
```

---

**For full documentation, see:**
- `MODULE_REFERENCE.md` - Complete module guide
- `TESTING_GUIDE.md` - Testing and validation
- `CONTRIBUTING.md` - Development guidelines
- `examples/` - Example scripts
- `notebooks/` - Jupyter Notebook examples

**Last Updated:** 2026-03-10
"""
