"""
MTR 5K (Arduino) Example
========================

Demonstrate how to use the routines to process downloaded mtr data.

Only for the 5k Arduino Series
"""
import EcoFOCIpy.io.mtr_parser as mtr_parser
import EcoFOCIpy.io.ncCFsave as ncCFsave
import EcoFOCIpy.metaconfig.load_config as load_config
import yaml

###############################################################
# edit to point to wpak raw datafile (arg parse?)
datafile = '../example_data/staticdata/'
instrument = ''
mooring_meta_file = '../example_data/mooring_example.yaml'
inst_meta_file = '../example_data/instr_metaconfig/mtr.yaml'
inst_shortname = 'mtr'
###############################################################

#init and load data
mtr = mtr_parser.mtrduino()
mtr_data = mtr.parse(filename=datafile,datetime_index=True) 
