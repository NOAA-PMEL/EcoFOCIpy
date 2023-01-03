# EcoFOCI
"""Contains a collection of pro-oceanus equipment parsing.
(A seabird product now)

These include:

TDGP - moored 

Non-moored:
* processing is likely the same if recording internally.

"""
import pandas as pd


class tdgp(object):
    r""" TDGP (Total Dissolved Gas Pressure) Unified parser

    """
    def __init__(self):
        """data is a pandas dataframe
        Wich is immediatly converted to xarray
        """
        pass
    
    def parse(self, filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read tdgp txt files

        Format:
        Measurement type,Year,Month,Day,Hour,Minute,Second,Pressure sensor temperature,Pressure (mbar),Supply Voltage

        Data (and variable names) are between "File Contents" and "Finished"
        """

        header = []
        fobj = []
        headercount = -2
        with open(filename) as fobj:
            for k, line in enumerate(fobj.readlines()):
                header = header + [line]
                if "File Contents:" in line:
                    headercount=k

                if (k == headercount+1):
                    column_names = line.strip().split(',')
                    break

        
 

        rawdata_df = pd.read_csv(filename, 
                        delimiter="\s+|,", 
                        skiprows=headercount+3, names=column_names, skipfooter=12)

        rawdata_df["date_time"] = pd.to_datetime(rawdata_df[['Day','Month','Year','Hour','Minute','Second']]
                       .astype(str).apply(' '.join, 1), format='%d %m %Y %H %M %S')
    
        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','Day','Month','Year','Hour','Minute','Second'],axis=1)        

        self.rawdata_df = rawdata_df

        return (rawdata_df,header)
