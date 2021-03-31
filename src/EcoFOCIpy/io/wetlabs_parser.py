# EcoFOCI
"""Contains a collection of wetlabs equipment parsing.
(A seabird product now)

These include:

Moored Eco and Wetstars:
* 1 channel -> 3 channel systems

Non-moored:
* processing is likely the same if recording internally.

"""
import pandas as pd
import sys

class wetlabs(object):
    r""" Wetlabs Unified parser
    
    EcoFLS(B) - single channel fluorometer (B-battery pack)
    EcoFLNT(US) - dual channel fluorometer and Trub
    Triplet - three channels

    Eco's have an array of channels to choose from... files are all the same,
    you must provide the right cal coefs for the data

    """

    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read fls(b) cnv files

        Wetlab format is Date Time Channel_Identifier Count TempCount
        """

        header = []
        with open(filename) as fobj:
            for k, line in enumerate(fobj.readlines()):
                header = header + [line]
                if "$get" in line:
                    headercount=k+2
                    break
        
 

        rawdata_df = pd.read_csv(filename, 
                        delimiter="\s+", 
                        parse_dates=True, 
                        header=None, 
                        skiprows=headercount)       

        if len(rawdata_df.columns) == 5: #single channel
           rawdata_df = rawdata_df.rename(columns={0: 'date',1:'time',3:str(rawdata_df[2][0]),4:'TempCount'})
           rawdata_df = rawdata_df.drop([2],axis=1)
        elif len(rawdata_df.columns) == 7: #two channel
           rawdata_df = rawdata_df.rename(columns={0: 'date',
                                                   1:'time',
                                                   3:str(rawdata_df[2][0]),
                                                   5:str(rawdata_df[4][0]),
                                                   6:'TempCount'})
           rawdata_df = rawdata_df.drop([2,4],axis=1)
        elif len(rawdata_df.columns) == 9: #three channel
           rawdata_df = rawdata_df.rename(columns={0: 'date',
                                                   1:'time',
                                                   3:str(rawdata_df[2][0]),
                                                   5:str(rawdata_df[4][0]),
                                                   7:str(rawdata_df[6][0]),
                                                   8:'TempCount'})
           rawdata_df = rawdata_df.drop([2,4,6],axis=1)
        else:
            print(f'number of channels unknown: {len(rawdata_df.columns)}')
            sys.exit()

        rawdata_df["date_time"] = pd.to_datetime(
            rawdata_df['date'] + " " + rawdata_df['time'], format="%m/%d/%y %H:%M:%S"
        )
        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time'],axis=1)        

        return (rawdata_df,header)

    def engr2sci(self,cal_coef=[],channels=1):
        """convert counts to quantity using wetlabs coefficients"""
        pass

    def time_correction(self,offset=None):
        """ apply a time offset in seconds"""
        pass