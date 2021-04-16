"""
FOCI 9/11+V2 Example
========================

Demonstrate how to use the routines to process downloaded 9/11+V2 CTD data.

Focus is on processing a single profile

To plot processed data - see "{}.ipynb" or example
"""

import yaml
import glob

import EcoFOCIpy.io.sbe_ctd_parser as sbe_ctd_parser #<- instrument specific
import EcoFOCIpy.io.ncCFsave as ncCFsave
import EcoFOCIpy.metaconfig.load_config as load_config

###############################################################
# edit to point to {cruise sepcific} raw datafiles 
sample_data_dir = '../'
datafile = sample_data_dir+'staticdata/example_data/profile_data/' #<- point to cruise and process all files within
cruise_name = 'DY1805' #no hyphens
cruise_meta_file = sample_data_dir+'staticdata/cruise_example.yaml'
inst_meta_file = sample_data_dir+'staticdata/instr_metaconfig/FOCI_standard_CTD.yaml'
group_meta_file = sample_data_dir+'staticdata/institutional_meta_example.yaml'
inst_shortname = ''
conscastno = 'ctd001.cnv'
###############################################################

#init and load data
cruise = sbe_ctd_parser.sbe9_11p()
filename_list = sorted(glob.glob(datafile + '*.cnv'))

(cruise_data,cruise_header) = cruise.parse(filename_list)

#example of a single profile
#- cruise_data['ctd001.cnv']

#get cruise info
with open(cruise_meta_file) as file:
    cruise_config = yaml.full_load(file)
cruise_config[cruise_name]


#and if you want a cast from the cruise, just use the consective cast number
#-  cruise_config['CTDCasts']['CTD001']

#get instrument info
with open(inst_meta_file) as file:
    inst_config = yaml.full_load(file)
inst_config


#*** biggest *** difference between moored and profile data is there may be multiple instruments with the same dataype (e.g.) temperature
# on the same platform.  We _used_ to use the phrases primary and secondary, but will now only refer to them as ch1, ch2 etc
cruise_data[conscastno] = cruise_data[conscastno].rename(columns={
                        't090C':'temperature_ch1',
                        't190C':'temperature_ch2',
                        'sal00':'salinity_ch1',
                        'sal11':'salinity_ch2',
                        'sbox0Mm/Kg':'oxy_conc_ch1',
                        'sbeox0ML/L':'oxy_concM_ch1',
                        'sbox1Mm/Kg':'oxy_conc_ch2',
                        'sbeox1ML/L':'oxy_concM_ch2',
                        'sbeox0PS':'oxy_percentsat_ch1',
                        'sbeox1PS':'oxy_percentsat_ch2',
                        'sigma-t00':'sigma_t_ch1',
                        'sigma-t11':'sigma_t_ch2',
                        'CStarAt0':'Attenuation',
                        'CStarTr0':'Transmittance',
                        'flECO-AFL':'chlor_fluorescence',
                        'turbWETntu0':'turbidity',
                        'empty':'empty', #this will be ignored
                        'flag':'flag'})

#get institutional information
with open(group_meta_file) as file:
    group_config = yaml.full_load(file)
group_config


# %%
# Add meta data and prelim processing based on meta data
# Convert to xarray and add meta information - save as CF netcdf file
# pass -> data, instmeta, depmeta
cruise_data_nc = ncCFsave.EcoFOCI_CFnc_profile(df=cruise_data[conscastno], 
                                instrument_yaml=inst_config, 
                                cruise_yaml=cruise_config)

cruise_data_nc.expand_dimensions()
cruise_data_nc.variable_meta_data(variable_keys=list(cruise_data[conscastno].columns.values),drop_missing=True)
cruise_data_nc.dimension_meta_data(variable_keys=['depth','latitude','longitude'])
cruise_data_nc.deployment_meta_add(conscastno=conscastno.split('.')[0].upper())

#add instituitonal global attributes
cruise_data_nc.institution_meta_add(group_config)

#add creation date/time - provenance data
cruise_data_nc.provinance_meta_add()

#provide intial qc status field
cruise_data_nc.qc_status(qc_status='unknown')

# %% [markdown]
# ## Save CF Netcdf files
# 
# Currently stick to netcdf3 classic... but migrating to netcdf4 (default) may be no problems for most modern purposes.  Its easy enough to pass the `format` kwargs through to the netcdf api of xarray.
cast = conscastno.split('.')[0].split('D')[-1]
cruise_data_nc.xarray2netcdf_save(xdf = cruise_data_nc.get_xdf(),
                           filename=cruise_data_nc.filename_const(manual_label=cruise_name+'c'+cast.zfill(3)+'_ctd'),format="NETCDF3_CLASSIC")

# ## Next Steps
# 
# QC of data (plot parameters with other instruments)
# - be sure to updated the qc_status and the history

