"""
WPAK Example
============

Demonstrate how to use the routines to process downloaded wpak data.

Not valid for argos data (NRT - only)
"""
import yaml

import src.EcoFOCIpy.io.wpak_parser as wpak_parser
import src.EcoFOCIpy.io.ncCFsave as ncCFsave
import src.EcoFOCIpy.metaconfig.load_config as load_config

###############################################################
# edit to point to wpak raw datafile (arg parse?)
datafile = 'staticdata/wpak_test.txt'
instrument = 'Weatherpak 1361'
mooring_meta_file = 'staticdata/mooring_example.yaml'
inst_meta_file = 'src/EcoFOCIpy/metaconfig/wpak_epickeys.yaml'
inst_shortname = 'wpak'
###############################################################

#init and load data
wpak = wpak_parser.wpak()
wpak_data = wpak.parse(filename=datafile,datetime_index=True) 

# time resample (or decimate)
### Choose one of the following two methods, or roll your own
## interpolate subroutines
"""
absolute simplest time gridding
 resample hourly will effectively truncate our times (only one data point in each hour)
 interpolate will fill some gaps
### like a time shift without adjusting data"""
wpak_grid_simple = wpak_data.resample('1H').mean().interpolate(limit=3)

"""
slightly more complex method - valid when data is far enough from the hour
 resample every 10min - but then linearly fill the supersampling
 then decimate to the hour
### very simple linear interpolation to hour"""
wpak_grid_decimate = wpak_data.resample('10T').mean().interpolate(limit=6)
wpak_grid_decimate = wpak_grid_decimate[wpak_grid_decimate.index.minute == 0]

#TODO: Output CSV file for NRT erddap? end initial/nrt processing ? lat/lon?

# Ingest instrumenttype parameter config file for meta information
# undefined variables in the data may not make it past this point if not 
#  given additional metainformation
inst_config = load_config.load_config(inst_meta_file)

# Ingest mooring yaml status file for deployment meta information
#  This provides deployment specific details.  The deployment files are 
#  created from the ecofoci-field database
#TODO: migrate db->yaml tool into this package
with open(mooring_meta_file) as file:
    mooring_config = yaml.full_load(file)

# Add meta data and prelim processing based on meta data
# Convert to xarray and add meta information - save as CF netcdf file
# pass -> data, instmeta, depmeta
wpak_nc = ncCFsave.EcoFOCI_CFnc_moored(df=wpak_grid_decimate, 
                                instrument_yaml=inst_config, 
                                mooring_yaml=mooring_config, 
                                instrument_id=instrument, 
                                inst_shortname=inst_shortname)

#add global attributes - not mandatory
wpak_nc.deployment_meta_add()
#add instituitonal global attributes
wpak_nc.institution_meta_add()
#add geospatial min/max data
wpak_nc.temporal_geospatioal_meta_data()

#add creation date/time - provenance data
wpak_nc.provinance_meta_add()

#provide intial qc status field
wpak_nc.qc_status(qc_status='unknown')

# combine trim (not mandatory) and filename together (saves to test.nc without name)
wpak_nc.xarray2netcdf_save(xdf = wpak_nc.autotrim_time(),
                           filename=wpak_nc.filename_const())

### tests 

def test_validate_mooringyaml_keys(yamlconfig):
    for mand_key in ['MooringID', 'Deployment', 'Recovery', 'Notes', 'Instrumentation']:
        assert mand_key in yamlconfig.keys(), f"{mand_key} not in Mooring Config file"

def test_sample_data_size(data=wpak_data):
    assert wpak_data.shape == (83, 13), 'test file not read in as expected - shape not right'

def test_instrument_in_mooring(instrument='Weatherpak', mooring_config=mooring_config):
    warning_text = 'Weatherpak not in mooring list, no meta info can be added'
    assert instrument in [x for x in mooring_config['Instrumentation']], warning_text    