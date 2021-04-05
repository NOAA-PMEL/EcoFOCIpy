# EcoFOCI
"""Contains a collection of seabird equipment parsing
specifically tailored to sbe-ctd operations.

These include:

Profile SBE (cnv files):
* 9/11+
* FastCats

"""
import pandas as pd
import ctd
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

class sbe9_11p(object):
    r""" Seabird 9/11+
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        There are quite a few instrument varations possible here - use the header meta to indentify variables

    """


    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read sbe9_11 .cnv files

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
