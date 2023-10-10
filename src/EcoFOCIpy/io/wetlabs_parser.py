# EcoFOCI
"""Contains a collection of wetlabs equipment parsing.
(A seabird product now)

These include:

Moored Eco and Wetstars:
* 1 channel -> 3 channel systems

Non-moored:
* processing is likely the same if recording internally.

"""
import sys

import datetime
import pandas as pd

class wetlabs(object):
    r""" Wetlabs Unified parser
    
    EcoFLS(B) - single channel fluorometer (B-battery pack)
    EcoFLNT(US) - dual channel fluorometer and Trub
    Triplet - three channels

    Eco's have an array of channels to choose from... files are all the same,
    you must provide the right cal coefs for the data

    """
    def __init__(self):
        """data is a pandas dataframe
        Wich is immediatly converted to xarray
        """
        pass
    
    def parse(self, filename=None, return_header=True, datetime_index=True):
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
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        self.rawdata_df = rawdata_df

        return (rawdata_df,header)

    def engr2sci(self,cal_coef={}):
        """convert counts to quantity using wetlabs coefficients
        
        requires a dictionary of dictionaries with {channel_name:{scaleF:0,darkCounts:0,name=None}}
        where channel_name = wavelength that the column gets labeled. scaleF and darkCounts are wetlabs
        provided cal coefficients and name is the measurement name (chlor, turb, scatter, CDOM, etc)
        """
        for channel in cal_coef.keys():
            try:
                self.rawdata_df[cal_coef[channel]['outname']] = cal_coef[channel]['scaleFactor'] * (self.rawdata_df[str(channel)]-cal_coef[channel]['darkCounts'])
            except:
                print(f'error with {channel}')
                pass #no data with that key

        return (self.rawdata_df)

    def time_correction(self,offset=None,method='offset_only'):
        """ apply a time offset in seconds
        
        To apply a temporal correction including drift, use method = 'linear'
        This method assumes the clock has been syncronized upon deployment."""
        if method == 'offset_only':
            self.rawdata_df.index = self.rawdata_df.index + pd.Timedelta(seconds=offset) 

        if method == 'linear':
            def lineartimecorr(x,deltaT,T0) :
                date = x + pd.Timedelta(seconds=((x -T0).total_seconds() * deltaT) )
                return date

            T0 = self.rawdata_df.index[0]
            deltaT = datetime.timedelta(seconds=offset) / (self.rawdata_df.index[-1] - T0)

            self.rawdata_df.index = self.rawdata_df.reset_index().apply(lambda x: lineartimecorr(x.date_time,deltaT,T0), axis=1)
            self.rawdata_df.index.name = 'date_time'

        return (self.rawdata_df)
    
    def NaT_removal(self):
        self.rawdata_df = self.rawdata_df.dropna()
