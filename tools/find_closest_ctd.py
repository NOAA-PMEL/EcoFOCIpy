#!/usr/bin/env python

"""
 FindClosestCTD.py
 
 Using the EcoFOCI ruise log database, search for CTD's within a specified range of a location


 History
 =======
 2024-02-06: Migrate to EcoFOCIpy Tools
 2019-07-15: Make python3 compliant: WIP

 Future
 ======

 Compatibility:
 ==============
 python >=3.8 **Tested

 """

import argparse
import datetime
import sys

import EcoFOCIpy.math.haversine as sphered
import numpy as np
from _dbconfig.EcoFOCI_db_io import EcoFOCI_db_datastatus

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2016, 9, 28)
__modified__ = datetime.datetime(2024, 2, 6)
__version__ = "0.1.1"
__status__ = "Development"


def read_data(db, cursor, table, yearrange):

    """

    """
    sql = (
        "SELECT `id`,`LatitudeDeg`,`LatitudeMin`,`LongitudeDeg`,"
        "`LongitudeMin`,`ConsecutiveCastNo`,`UniqueCruiseID`,`GMTDay`,"
        "`GMTMonth`,`GMTYear`,`MaxDepth` from `{table}` WHERE `GMTYear` BETWEEN '{startyear}' AND '{endyear}'"
    ).format(table=table, startyear=yearrange[0], endyear=yearrange[1])
    print(sql)

    result_dic = {}
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Get column names
        rowid = {}
        counter = 0
        for i in cursor.description:
            rowid[i[0]] = counter
            counter = counter + 1
        # print rowid
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            result_dic[row["UniqueCruiseID"] + "_" + row["ConsecutiveCastNo"]] = {
                keys: row[keys] for val, keys in enumerate(row.keys())
            }
        return result_dic
    except:
        print("Error: unable to fecth data")


def read_mooring(db, cursor, table, MooringID):
    sql = ("SELECT * from `{0}` WHERE `MooringID`= '{1}' ").format(table, MooringID)

    result_dic = {}
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Get column names
        rowid = {}
        counter = 0
        for i in cursor.description:
            rowid[i[0]] = counter
            counter = counter + 1
        # print rowid
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            result_dic[row["MooringID"]] = {
                keys: row[keys] for val, keys in enumerate(row.keys())
            }
        return result_dic
    except:
        print("Error: unable to fecth data")


"""------------------------------------------------------------------------------------"""
parser = argparse.ArgumentParser(
    description="Find Closest CTD casts to Mooring Deployment"
)

parser.add_argument(
    "DistanceThreshold",
    metavar="DistanceThreshold",
    type=float,
    help="Distance From Mooring in Kilometers",
)
parser.add_argument(
    "YearRange",
    metavar="YearRange",
    type=int,
    nargs=2,
    help="Range of years to look (eg 2012 2014)",
)
parser.add_argument(
    "-db_moor",
    "--db_moorings",
    type=str,
    help="path to db .pyini file for mooring records",
    default='_secret/db_config_mooring.yaml'
)
parser.add_argument(
    "-db_ctd", 
    "--db_ctd", 
    type=str, 
    help="path to db .pyini file for ctd records",
    default='_secret/db_config_cruises.yaml'
)
parser.add_argument(
    "-MooringID", metavar="--MooringID", type=str, help="MooringID 13BSM-2A"
)
parser.add_argument(
    "-latlon",
    "--latlon",
    nargs="+",
    type=float,
    help="use manual lat/lon (decimaldegrees +N,+W)",
)

args = parser.parse_args()

if not args.latlon and not args.MooringID:
    print("Choose either a mooring location or a lat/lon pairing")
    sys.exit()

if args.latlon:  # manual input of lat/lon
    location = [args.latlon[0], args.latlon[1]]

if args.MooringID:
    # get db meta information for mooring
    ### connect to DB
    EcoFOCI_db = EcoFOCI_db_datastatus()
    (db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=args.db_moorings)
    table = "mooringdeploymentlogs"
    Mooring_Meta = read_mooring(db, cursor, table, args.MooringID)
    EcoFOCI_db.close()


    # location = [71 + 13.413/60., 164 + 14.98/60.]
    location = [
        float(Mooring_Meta[args.MooringID]["Latitude"].split()[0])
        + float(Mooring_Meta[args.MooringID]["Latitude"].split()[1]) / 60.0,
        float(Mooring_Meta[args.MooringID]["Longitude"].split()[0])
        + float(Mooring_Meta[args.MooringID]["Longitude"].split()[1]) / 60.0,
    ]


threshold = args.DistanceThreshold  # km

# get db meta information for mooring
### connect to DB
EcoFOCI_db = EcoFOCI_db_datastatus()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=args.db_ctd)
table = "cruisecastlogs"
cruise_data = read_data(db, cursor, table, args.YearRange)
EcoFOCI_db.close()

for index in sorted(cruise_data.keys()):

    destination = [
        cruise_data[index]["LatitudeDeg"] + cruise_data[index]["LatitudeMin"] / 60.0,
        cruise_data[index]["LongitudeDeg"] + cruise_data[index]["LongitudeMin"] / 60.0,
    ]
    Distance2Station = sphered.distance(location, destination)

    if Distance2Station <= threshold:
        print(
            "Cast {0} on Cruise {1} is {2:3.2f} km away - {3}-{4}-{5} and {6}m deep".format(
                cruise_data[index]["ConsecutiveCastNo"],
                cruise_data[index]["UniqueCruiseID"],
                Distance2Station,
                cruise_data[index]["GMTYear"],
                cruise_data[index]["GMTMonth"],
                cruise_data[index]["GMTDay"],
                cruise_data[index]["MaxDepth"],
            )
        )
