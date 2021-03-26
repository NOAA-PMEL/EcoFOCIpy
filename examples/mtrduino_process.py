"""
MTR 5K (Arduino) Example
========================

Demonstrate how to use the routines to process downloaded mtr data.

Only for the 5k Arduino Series
"""
import yaml

import EcoFOCIpy.io.mtr_parser as mtr_parser
import EcoFOCIpy.io.ncCFsave as ncCFsave
import EcoFOCIpy.metaconfig.load_config as load_config

###############################################################
# edit to point to wpak raw datafile (arg parse?)
datafile = '../staticdata/'
instrument = ''
mooring_meta_file = '../staticdata/mooring_example.yaml'
inst_meta_file = '../staticdata/instr_metaconfig/mtr.yaml'
inst_shortname = 'mtr'
###############################################################

#init and load data
mtr = mtr_parser.mtrduino()
mtr_data = mtr.parse(filename=datafile,datetime_index=True) 