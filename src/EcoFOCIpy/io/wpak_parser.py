"""Contains a collection of WPAK equipment parsing.

These include:

* ARGO Transmitted
* Internally Recorded

    usage: where src=instrument class
    fobj = src.get_data(filename, MooringID)
    Dataset = src.parse(fobj, **kwargs)
"""
import pandas as pd


class wpak(object):
    r""" MetOcean WeatherPak
    
    remove software lines up to header-row for downloaded data - add test for this

    see staticdata/wpak_test.txt for example
    """

    @staticmethod
    def parse(filename=None, argos_file=False, datetime_index=True):
        r"""
        Basic Method to open and read wpak csv files 

        Alternatively we can pass ARGOS retrieved data in 

        Default pass the pandas dataframe back indexed by datetime

        returns pandas dataframe
        """
        assert filename != None , 'Must provide a datafile'

        rawdata_df = pd.read_csv(filename, header=0, delimiter=r'\s+')
        rawdata_df["date_time"] = pd.to_datetime(
            rawdata_df["DATE"] + " " + rawdata_df["TIME"], format="%y/%m/%d %H:%M:%S"
        )

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','DATE','TIME'],axis=1)

        return rawdata_df
