"""Contains a collection of MTR equipment parsing.

These include:

* Version 3/4 (old version) [ ]
* Version 5 (MTRduino) [x]

"""
import pandas as pd


class rcm(object):
    r""" Anderaa instruments (RCM 4, 7, 9, 11's
    EcoFOCI QC procedure developed by Dave P. and done within excel spreadsheet

    Dave P. usually performed the engr conversions and trimmed the data via excel
    Also calculated parameters to monitor the health of the rcm during deployment

    For now... stick to excel qc procedure, and just archive exceldata
    TODO: This should be a replacement of the original rcm mooring analyis software"""

    @staticmethod
    def parse_excel(filename=None, datetime_index=True):
        r"""
        Basic Method to open and read rcm excel files
        """

        rawdata_df = pd.read_excel(filename, skiprows=4, parse_dates=["date/time"], index_col="date/time")
        rawdata_df.rename_axis("date_time", inplace=True)

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time',"date/time"],axis=1)        

        return rawdata_df

class rcm_sg(object):    
    r""" Anderaa instruments (RCM Seaguards
    These datastreams are no longer binary off the instrument and can be qc'd by the aandera software,
    This means that a preliminary qc'd product is archived in netcdf via output files.

    Due to the Seaguard being a platform, multiple datafiles are possible, usually including oxygen but not always

    TODO: This should be a replacement of the original rcm mooring analyis software"""

    @staticmethod
    def parse_excel(filename=None, datetime_index=True):
        r"""
        Basic Method to open and read rcm excel files
        """

        rawdata_df = pd.read_csv(filename, header=1, delimiter="\t")
        rawdata_df["date_time"] = pd.to_datetime(rawdata_df["Time tag (Gmt)"], format="%d.%m.%y %H:%M:%S")

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','Time tag (Gmt)'],axis=1)        

        return rawdata_df
