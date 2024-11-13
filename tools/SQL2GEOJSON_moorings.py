"""
 SQL2GEOJSON_Moorings.py
 
export all mooring locations to geojson format for plotting

 Input: MooringID (eg. 14bsm2a or 14BSM-2A)
 Output: geojson file with

History:
=======

Compatibility:
==============
python >=3.6 - Tested


"""

import argparse
import datetime

import numpy as np
from _dbconfig.EcoFOCI_db_io import EcoFOCI_db_datastatus

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2015, 5, 28)
__modified__ = datetime.datetime(2024, 11, 13)
__version__ = "0.2.0"
__status__ = "Development"
__keywords__ = "moorings", "csv", "heatmap", "geojson"

"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(
    description="Mooring Database -> GEOJSON For currently deployed"
)
parser.add_argument(
    "-db",
    "--db_ini",
    type=str,
    help="path to db .yaml file",
    default="_secret/db_config_mooring.yaml",
)
parser.add_argument("--geojson", action="store_true", help="create geojson file")
parser.add_argument("--all", action="store_true", help="create files for all moorings")

args = parser.parse_args()


EcoFOCI_db = EcoFOCI_db_datastatus()
(db, cursor) = EcoFOCI_db.connect_to_DB(db_config_file=args.db_ini)

if args.all:
    table = "mooringdeploymentlogs"
    data_mooring = EcoFOCI_db.read_mooring_summary(
        table=table
    )
else:
    table = "mooringdeploymentlogs"
    data_mooring = EcoFOCI_db.read_mooring_summary(
        table=table, deployed=True, verbose=False
    )

# find missing or undeployed data and skip
for a_ind in data_mooring.keys():
    if (
        (data_mooring[a_ind]["Latitude"] == "")
        or (data_mooring[a_ind]["Latitude"] == "NOT DEPLOYED")
        or not (data_mooring[a_ind]["Latitude"])
    ):
        data_mooring[a_ind]["Latitude"] = "00 0.00 N"
        data_mooring[a_ind]["Longitude"] = "00 0.00 W"

mooring_lat = np.array(
    [
        float(data_mooring[a_ind]["Latitude"].split()[0])
        + float(data_mooring[a_ind]["Latitude"].split()[1]) / 60.0
        for a_ind in data_mooring.keys()
    ]
)
mooring_lon = np.array(
    [
        -1.0
        * (
            float(data_mooring[a_ind]["Longitude"].split()[0])
            + float(data_mooring[a_ind]["Longitude"].split()[1]) / 60.0
        )
        for a_ind in data_mooring.keys()
    ]
)
mooringid = data_mooring.keys()

if args.geojson:
    # "Generating .geojson"
    geojson_header = '{"type": "FeatureCollection","features": ['
    geojson_point_coords = ""

    for k, _value in enumerate(mooring_lat):
        if (mooring_lat[k] != 0.0) and (mooring_lon[k] != 0.0):
            geojson_point_coords = geojson_point_coords + (
                """{{"type": "Feature","geometry": {{"type": "Point","coordinates": [{1},{0}]}}, "properties": {{"MooringID":"<a href='http://ecofoci-field.pmel.noaa.gov/bell/eFOCI_Mooring_logs/mooring_record_view.php?mooringview_id={2}'>{2}</a>" }}}}"""
            ).format(mooring_lat[k], mooring_lon[k], list(mooringid)[k])

            if k + 1 != len(mooring_lat):
                geojson_point_coords = geojson_point_coords + ", "

    geojson_tail = "]\n" "}\n"

    print(f"{geojson_header}{geojson_point_coords}{geojson_tail}")
