# EcoFOCI
"""Contains a collection of seabird equipment parsing.

These include:

Moored SBE (cnv files):
* 16,19,26,37,39,56

"""
import pandas as pd
import sys

# Temp, Press, Sal, Cond
class sbe37(object):
    r""" Seabird 37 Microcat CTD (with optional pressure)
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        With or without header

        With or without pressure - assume 6 cols = w/press, 5 cols = w/o press.  There is at least one unit that does not 
        automatically output salinity, but does have pressure - thus it has only 4 columns.  It needs to be treated
        specially.

    """

    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read sbe37 csv files

        """
        assert filename != None , 'Must provide a datafile'

        header = []

        with open(filename) as fobj:
            for k, line in enumerate(fobj.readlines()):
                header = header + [line]
                if "*END*" in line:
                    headercount=k+4
                    break


        rawdata_df = pd.read_csv(filename, 
                        delimiter=",", 
                        parse_dates=True, 
                        header=None, 
                        skiprows=headercount)

        #column names must be consistent with later used CF variable names (not the standard names, just the variable names)
        if len(rawdata_df.columns) == 6: #T,C,P,S
            rawdata_df.columns = ['temperature','conductivity','pressure','salinity','date','time']
        elif len(rawdata_df.columns) == 5: #T,C,S or maybe T,C,P
            rawdata_df.columns = ['temperature','conductivity','salinity','date','time']
        else:
            sys.exit(f'Unknown number of columns in raw data {len(rawdata_df.columns)}')


        rawdata_df["date_time"] = pd.to_datetime(rawdata_df["date"] + " " + rawdata_df["time"], format=" %d %b %Y %H:%M:%S")

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        return (rawdata_df,header)

# Temp, Press
class sbe39(object):
    r""" Seabird 39 Temperature (with optional pressure)
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        With or without header

        With or without pressure - assume 4 cols = w/press, 3 cols = w/o press

    """

    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read sbe39 csv files

        """
        assert filename != None , 'Must provide a datafile'

        header = []

        with open(filename) as fobj:
            for k, line in enumerate(fobj.readlines()):
                header = header + [line]
                if "*END*" in line:
                    headercount=k+4
                    break


        rawdata_df = pd.read_csv(filename, 
                        delimiter=",", 
                        parse_dates=True, 
                        header=None, 
                        skiprows=headercount)

        #column names must be consistent with later used CF variable names (not the standard names, just the variable names)
        if len(rawdata_df.columns) == 4:
            rawdata_df.columns = ['temperature','pressure','date','time']
        elif len(rawdata_df.columns) == 3:
            rawdata_df.columns = ['temperature','date','time']
        else:
            sys.exit('Unknown number of columns in raw data')

        rawdata_df["date_time"] = pd.to_datetime(rawdata_df["date"] + " " + rawdata_df["time"], format=" %d %b %Y %H:%M:%S")

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        return (rawdata_df,header)

