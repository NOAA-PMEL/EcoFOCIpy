# EcoFOCI
"""Contains a collection of seabird equipment parsing.

These include:

Moored SBE (cnv files):
* 16,19,26,37,39,56

"""
import pandas as pd
import sys
import datetime

def sbetime_conversion(time_type='timeJ',data=None):
    """Seabird offers multiple time output options:
    timeJ:
    timeS:
    timeJV2:
    """
    pass

def seabird_header(filename=None):
    r""" Seabird Instruments have a header usually defined by *END with a significant amount of
    information imbedded.  Send a flag to parse seabird headers.  Better yet may be to combine seabird gear
    into classes and subclasses.
    """
    assert filename.split('.')[-1] == 'cnv' , 'Must provide a tid file - use sbe software to convert'

    header = []
    var_names = {}
    with open(filename) as fobj:
        for k, line in enumerate(fobj.readlines()):
            header = header + [line]
            if "# name" in line:
                var_names[int(line.split("=")[0].split()[-1])] = line.split("=")[1].split()[0].split(':')[0]
            if "# start_time" in line:
                start_time = line.split("[")[0].split("=")[-1].strip()
            if "*END*" in line:
                headercount=k+1
                break

    return (header, headercount, var_names, start_time)

class sbe16(object):
    r""" Seabird 16
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        There are quite a few instrument varations possible here - use the header meta to indentify variables

    """


    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read sbe16 .cnv files

        """
        assert filename.split('.')[-1] == 'cnv' , 'Must provide a cnv file - use sbe software to convert'

        header = []
        var_names = {}
        with open(filename) as fobj:
            for k, line in enumerate(fobj.readlines()):
                header = header + [line]
                if "# name" in line:
                    var_names[int(line.split("=")[0].split()[-1])] = line.split("=")[1].split()[0].split(':')[0]
                if "# start_time" in line:
                    start_time = line.split("[")[0].split("=")[-1].strip()
                if "*END*" in line:
                    headercount=k+1
                    break


        rawdata_df = pd.read_csv(filename, 
                        delimiter="\s+", 
                        parse_dates=True, 
                        header=None,
                        names=var_names.values(), 
                        skiprows=headercount)

        if 'timeJ' in var_names.values():
            rawdata_df['date_time'] = [datetime.datetime.strptime(start_time, "%b %d %Y %H:%M:%S") + pd.Timedelta(days=x) for x in rawdata_df['timeJ']]
        elif 'timeJV2' in var_names.values():
            rawdata_df['date_time'] = [datetime.datetime.strptime(start_time, "%b %d %Y %H:%M:%S") + pd.Timedelta(days=x) for x in rawdata_df['timeJV2']]
        elif 'timeS' in var_names.values():
            rawdata_df['date_time'] = [datetime.datetime.strptime(start_time, "%b %d %Y %H:%M:%S") + pd.Timedelta(seconds=x) for x in rawdata_df['timeS']]
        else:
            print(f'no time index identified: {var_names.values()}')

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time'],axis=1)        

        return (rawdata_df,header)

class sbe26(object):
    r""" Seabird 26 Wave and Tide GuageTemperature (with optional pressure)
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

    """

    @staticmethod
    def parse(filename=None, datetime_index=True):
        r"""
        Basic Method to open and read sbe26 .tid files

        """
        assert filename.split('.')[-1] == 'tid' , 'Must provide a tid file - use sbe software to convert'

        rawdata_df = pd.read_csv(filename, 
                                 delimiter="\s+", 
                                 skiprows=1, 
                                 names=["date", "time", "pressure", "temperature"])
        
        
        rawdata_df["date_time"] = pd.to_datetime(rawdata_df["date"] + " " + rawdata_df["time"], format="%m/%d/%Y %H:%M:%S")

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        return (rawdata_df)

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

# Temp
class sbe56(object):
    r""" Seabird 56 Temperature 
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        With or without header

        No pressure, all cnv files are 4 columns (count, time, temp, flag)

    """

    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read sbe56 cnv files

        Similar to sbe9 cnv files with varying time descriptions
        timeJ = Julian date (from start date)

        TODO: more than one time column or columns based on names
        """
        assert filename != None , 'Must provide a datafile'
        assert filename.split('.')[-1] == 'cnv' , 'Must provide a cnv file - use sbe software to convert'

        header = []
        var_names = {}
        with open(filename) as fobj:
            for k, line in enumerate(fobj.readlines()):
                header = header + [line]
                if "# name" in line:
                    var_names[int(line.split("=")[0].split()[-1])] = line.split("=")[1].split()[0].split(':')[0]
                if "# start_time" in line:
                    start_time = line.split("[")[0].split("=")[-1].strip()
                if "*END*" in line:
                    headercount=k+1
                    break


        rawdata_df = pd.read_csv(filename, 
                        delimiter="\s+", 
                        parse_dates=True, 
                        header=None, 
                        skiprows=headercount)


        #column names must be consistent with later used CF variable names (not the standard names, just the variable names)
        if len(rawdata_df.columns) == 4:
            rawdata_df.columns = ['index','time_param','temperature','flag']
        else:
            sys.exit('Unknown number of columns in raw data')

        #time deffinition selector

        if 'timeJ' in var_names.values():
            rawdata_df['date_time'] = [datetime.datetime.strptime(start_time, "%b %d %Y %H:%M:%S") + pd.Timedelta(days=x) for x in rawdata_df['time_param']]
        elif 'timeS' in var_names.values():
            rawdata_df['date_time'] = [datetime.datetime.strptime(start_time, "%b %d %Y %H:%M:%S") + pd.Timedelta(seconds=x) for x in rawdata_df['time_param']]
        else:
            print(f'no time index identified: {var_names.values()}')

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','time_param'],axis=1)        

        return (rawdata_df,header)

