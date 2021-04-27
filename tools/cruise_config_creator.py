"""
 DBMooringSummary.py
 
 Input: CruiseID (eg. 14bsm2a or 14BSM-2A)
 Output: text file with...
    mooring charactersistcs
    instruments deployed, depths, serial numbers

History:
=======

Compatibility:
==============
python >=3.6 - Tested


"""

import argparse
import datetime
import sys

import yaml
from _dbconfig.EcoFOCI_db_io import EcoFOCI_db_datastatus
from EcoFOCIpy.math.geotools import latlon_convert
from EcoFOCIpy.metaconfig import load_config

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 1, 13)
__modified__ = datetime.datetime(2021, 3, 24)

"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(description='Cruise Meta Builder - outputs a parsed text \
                                              of meta information unless the yaml flag is provided')
parser.add_argument('CruiseID', metavar='CruiseID', type=str, help='CruiseID of form dy1908')               
parser.add_argument('-db', '--db_ini', 
                    type=str, 
                    help='path to db .yaml file', 
                    default='_secret/db_config_cruise.yaml')               
parser.add_argument('-yaml', '--yaml_format', 
                    action="store_true", 
                    help='format for yaml files')               

args = parser.parse_args()
 
#its a view only user so hardcoding is ok... config file needs to be edited if
#  machine changes
config_file = '_secret/db_config_cruises.yaml'

EcoFOCI_db = EcoFOCI_db_datastatus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

table = 'cruises'
Cruise_Meta_sum = EcoFOCI_db.read_cruise_summary(table=table, cruiseid=args.CruiseID, verbose=True)
table = 'cruisecastlogs'
Cruise_Castlogs_sum = EcoFOCI_db.read_castlog_summary(table=table, cruiseid=args.CruiseID)

EcoFOCI_db.close()


#replace timedelta with strings
for entries in sorted(Cruise_Castlogs_sum.keys()):
    for subentries in (Cruise_Castlogs_sum[entries].keys()):
        try:
            if isinstance(Cruise_Castlogs_sum[entries][subentries], datetime.timedelta):
                Cruise_Castlogs_sum[entries][subentries] = (Cruise_Castlogs_sum[entries][subentries]).seconds
        except:
            pass

if args.yaml_format:

    try:
        #build a dictionary of dictionaries for ctd casts
        CTDDic = {}
        for profile in sorted(Cruise_Castlogs_sum.keys()):
            CTDDic[profile] = Cruise_Castlogs_sum[profile]
            
        Cruise_Meta_sum.update({"CTDCasts":CTDDic})
    except:
        print("An issue exists in the CTDcasts records")
        sys.exit()        

    load_config.write_config(args.CruiseID+'.yaml', Cruise_Meta_sum)
