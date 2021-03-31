"""
SBE37 Example
=============
Demonstrate how to use the routines to process downloaded sbe37 cnv data
Usable as a template for all other sbe-39 processing

* with pressure and without pressure

See Jupyter Notebook for commentary, walkthrough, and output
"""
import yaml

import EcoFOCIpy.io.sbe_parser as sbe_parser
import EcoFOCIpy.io.ncCFsave as ncCFsave
import EcoFOCIpy.metaconfig.load_config as load_config

###############################################################
# edit to point to wpak raw datafile (arg parse?)
datafile = '../example_data/staticdata/sbe37_wpress.cnv'
instrument = 'SBE-37 1807'
mooring_meta_file = '../example_data/mooring_example.yaml'
inst_meta_file = '../example_data/instr_metaconfig/sbe37_cf.yaml'
inst_shortname = 's37'
###############################################################

#init and load data
sbe37_wop = sbe_parser.sbe37()
(sbe37_wop_data,sbe37_wop_header) = sbe37_wop.parse(filename=datafile,
                                                    return_header=True,
                                                    datetime_index=True) 

##### time frequency adjustment
# this step can be done at any point and is usually a small shift for
# most instruments
#####

#round off times to nearest sample frequency
sbe37_wop_data.index = sbe37_wop_data.index.round(freq='10min')
#resample to fix non-monotonic times (missing data) and fill linearly up to one hour
sbe37_wop_data = sbe37_wop_data.resample('10min').mean().interpolate(limit=6)

# Ingest instrumenttype parameter config file for meta information
# undefined variables in the data may not make it past this point if not 
#  given additional metainformation
with open(inst_meta_file) as file:
    inst_config = yaml.full_load(file)

# Ingest mooring yaml status file for deployment meta information
#  This provides deployment specific details.  The deployment files are 
#  created from the ecofoci-field database
#TODO: migrate db->yaml tool into this package
with open(mooring_meta_file) as file:
    mooring_config = yaml.full_load(file)

# Add meta data and prelim processing based on meta data
# Convert to xarray and add meta information - save as CF netcdf file
# pass -> data, instmeta, depmeta
### 1
sbe37_wop_nc = ncCFsave.EcoFOCI_CFnc_moored(df=sbe37_wop_data, 
                                instrument_yaml=inst_config, 
                                mooring_yaml=mooring_config, 
                                instrument_id=instrument, 
                                inst_shortname=inst_shortname)

#Following section is "optional" in the sense that not performing any of the steps will still
# lead to a functional file, but just without much metadata... eg... (1,2) can be done to have a 
# quicklook available... and temp config files can also be easily created in the same pattern
# as the official ones.
#--------------------------------------------------------------------------------------#
# expand the dimensions and coordinate variables
# renames them appropriatley and prepares them for meta-filled values
sbe37_wop_nc.expand_dimensions()

sbe37_wop_nc.variable_meta_data(variable_keys=['temperature'])
sbe37_wop_nc.temporal_geospatioal_meta_data(depth='designed')
#adding dimension meta needs to come after updating the dimension values... BUG?
sbe37_wop_nc.dimension_meta_data(variable_keys=['depth','latitude','longitude'])

#add global attributes
sbe37_wop_nc.deployment_meta_add()
sbe37_wop_nc.get_xdf()

#add instituitonal global attributes
sbe37_wop_nc.institution_meta_add()

#add creation date/time - provenance data
sbe37_wop_nc.provinance_meta_add()

#provide intial qc status field
sbe37_wop_nc.qc_status(qc_status='unknown')
#--------------------------------------------------------------------------------------#

### 2
# combine trim (not mandatory) and filename together (saves to test.nc without name)
sbe37_wop_nc.xarray2netcdf_save(xdf = sbe37_wop_nc.autotrim_time(),
                           filename=sbe37_wop_nc.filename_const(depth='designed'),format="NETCDF3_CLASSIC")


