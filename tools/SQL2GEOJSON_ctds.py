"""
 SQL2GEOJSON_ctds.py
 
export all ctd locations to geojson format for plotting

 Output: geojson file with

History:
=======

Compatibility:
==============
python >=3.9 - Tested


"""

import argparse
import datetime

import numpy as np
from _dbconfig.EcoFOCI_db_io import EcoFOCI_db_datastatus

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2015, 5, 28)
__modified__ = datetime.datetime(2025, 4, 9)
__version__ = "0.2.0"
__status__ = "Development"
__keywords__ = "ctds", "csv", "heatmap", "geojson"

"""------------------------------- MAIN ----------------------------------------"""

parser = argparse.ArgumentParser(
    description="Cruise Database -> GEOJSON For all CTDs"
)
parser.add_argument(
    "-db",
    "--db_ini",
    type=str,
    help="path to db .yaml file",
    default="_secret/db_config_cruises.yaml",
)
parser.add_argument("--geojson", action="store_true", help="create geojson file")

args = parser.parse_args()


EcoFOCI_db = EcoFOCI_db_datastatus()
(db, cursor) = EcoFOCI_db.connect_to_DB(db_config_file=args.db_ini)

table = "cruisecastlogs"
data_cruise = EcoFOCI_db.read_cruise(
    table=table
)

cruises_lat = np.array(
    [
        float(data_cruise[a_ind]["LatitudeDeg"])
        + float(data_cruise[a_ind]["LatitudeMin"]) / 60.0
        for a_ind in data_cruise.keys()
    ]
)
cruises_lon = np.array(
    [
        -1.0
        * (
            float(data_cruise[a_ind]["LongitudeDeg"])
            + float(data_cruise[a_ind]["LongitudeMin"]) / 60.0
        )
        for a_ind in data_cruise.keys()
    ]
)
mooringid = [ data_cruise[a_ind]['UniqueCruiseID'] for a_ind in data_cruise.keys()]

if args.geojson:
    # "Generating .geojson"
    geojson_header = '{"type": "FeatureCollection","features": ['
    geojson_point_coords = ""

    for k, _value in enumerate(cruises_lat):
        if (cruises_lat[k] != 0.0) and (cruises_lon[k] != 0.0):
            geojson_point_coords = geojson_point_coords + (
                """{{"type": "Feature","geometry": {{"type": "Point","coordinates": [{1},{0}]}}, "properties": {{"CruiseID":"{2}" }}}}"""
            ).format(cruises_lat[k], cruises_lon[k], list(mooringid)[k])

            if k != len(cruises_lat) - 1:
                geojson_point_coords = geojson_point_coords + ", "

    geojson_tail = "]\n" "}\n"

    print(f"{geojson_header}{geojson_point_coords}{geojson_tail}")
