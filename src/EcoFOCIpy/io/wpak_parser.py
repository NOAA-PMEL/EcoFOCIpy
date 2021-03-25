"""Contains a collection of WPAK equipment parsing.

These include:

* ARGO Transmitted
* Internally Recorded

    usage: where src=instrument class
    fobj = src.get_data(filename, MooringID)
    Dataset = src.parse(fobj, **kwargs)
"""
from io import BytesIO

import pandas as pd


class wpak(object):
    r""" MetOcean WeatherPak
    
    remove software lines up to header-row for downloaded data

    see staticdata/wpak_test.txt for example
    """

    @staticmethod
    def get_data(filename=None, **kwargs):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments
        """

        fobj = open(filename)
        data = fobj.read()

        buf = data
        return BytesIO(buf.strip())

    @staticmethod
    def parse(fobj, argos_file=False):
        r"""
        Basic Method to open and read wpak csv files 

        Alternatively we can pass ARGOS retrieved data in 

        returns pandas dataframe
        """

        rawdata_df = pd.read_csv(fobj, header=0, delimiter="s+")
        rawdata_df["date_time"] = pd.to_datetime(
            rawdata_df["DATE"] + " " + rawdata_df["TIME"], format="%y/%m/%d %H:%M:%S"
        )

        return rawdata_df
