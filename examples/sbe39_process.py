"""
SBE39 Example
=============

Demonstrate how to use the routines to process downloaded sbe39 cnv data

* with pressure and without pressure

"""
import yaml

import EcoFOCIpy.io.sbe_parser as sbe_parser
import EcoFOCIpy.io.ncCFsave as ncCFsave
import EcoFOCIpy.metaconfig.load_config as load_config

###############################################################
# edit to point to wpak raw datafile (arg parse?)
datafile = '../staticdata/sbe39_wopress.cnv'
instrument = 'SBE-39 1777'
mooring_meta_file = '../staticdata/mooring_example.yaml'
inst_meta_file = '../staticdata/instr_metaconfig/sbe39_cf.yaml'
inst_shortname = 's39'
###############################################################

#init and load data
sbe39_wop = sbe_parser.sbe39()
(sbe39_wop_header,sbe39_wop_data) = sbe39_wop.parse(filename=datafile,
                                                    return_header=True,
                                                    datetime_index=True) 