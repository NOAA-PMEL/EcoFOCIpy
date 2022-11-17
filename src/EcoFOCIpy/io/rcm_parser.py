"""Contains a collection of MTR equipment parsing.

These include:

* Version 3/4 (old version) [ ]
* Version 5 (MTRduino) [x]

"""
import numpy as np
import pandas as pd


class rcm_excel(object):
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

class rcm(object):
    r"""
    Evolution of the old RCM 7/9/11 Procedure.  Output *.dsu file to *.dat (tsv/csv) and process without excel worksheets.

    Some notes below to convert dsu recorded counts to engr units.
    RCM Oxygen 0.4883*counts = concentration (with internally set salinity.  FOCI standard is 0PSU).  D.Pashinski also had an equation to calculate percent saturation, but this needs to be validated? Ultimately, recalculate after salinity correction is applied.

    Pressure, Turb, Cond/Sal, Temp have a transfer equation and coefs that need to be applied and these are unique to each unit (oxy are cal'd on instrument ad output a scaled value that is rcm independent, U/V comps are cal'd to the board and also output a alue that is already scaled)
    """

    def parse(self, filename=None, number_of_channels=8, time_format=0, datetime_index=True):
        r"""
        Basic Method to open and read converted dsu files 

        time_format: 0 - %m/%d/%Y %H:%M:%S
        time_format: 1 - %d.%m.%Y %H:%M:%S

        returns pandas dataframe
        """
        assert filename != None , 'Must provide a datafile'
        assert time_format <=1 , 'time_format must be 0,1'
        if number_of_channels == 8:
            headernames=['sample','date','time','ident','speed_engr','dir_engr','temp_engr','cond_engr','press_engr','chan7','chan8']
        elif number_of_channels == 7:
            headernames=['sample','date','time','ident','speed_engr','dir_engr','temp_engr','cond_engr','press_engr','chan7']
        else:
            headernames=['sample','date','time','ident','speed_engr','dir_engr','temp_engr','cond_engr','press_engr']

        rawdata_df = pd.read_csv(filename, names=headernames, delimiter="\s+",)
        if time_format == 0:
            rawdata_df["date_time"] = pd.to_datetime(
                rawdata_df['date'] + " " + rawdata_df['time'], format="%m/%d/%Y %H:%M:%S"
            )
        elif time_format == 1:
            rawdata_df["date_time"] = pd.to_datetime(
                rawdata_df['date'] + " " + rawdata_df['time'], format="%d.%m.%Y %H:%M:%S"
            )
        else:
            pass
        rawdata_df['temp_engr'] = pd.to_numeric(rawdata_df['temp_engr'],errors='coerce')

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time','date','time'],axis=1)

        self.rawdata_df = rawdata_df

        return (self.rawdata_df)

    def engr2sci_curr(self):
        """
        Convert speed/dir

        """
        self.rawdata_df['current_speed'] = self.rawdata_df['speed_engr']*0.2933
        self.rawdata_df['current_direction_uncorrected'] = self.rawdata_df['dir_engr']*0.3515
        self.rawdata_df['u_curr_comp'] = self.rawdata_df['current_speed']*np.sin(np.deg2rad(self.rawdata_df['current_direction_uncorrected']))
        self.rawdata_df['v_curr_comp'] = self.rawdata_df['current_speed']*np.cos(np.deg2rad(self.rawdata_df['current_direction_uncorrected']))

    def engr2sci_oxy(self,channel='chan8'):
        """
        Convert speed/dir

        """
        if channel=='chan8':
            self.rawdata_df['oxy_conc'] = self.rawdata_df['chan8']*0.4883
        elif channel=='chan7':
            self.rawdata_df['oxy_conc'] = self.rawdata_df['chan7']*0.4883

    def engr2sci_temp(self,coefA=0,coefB=0,coefC=0,coefD=0):
        """
        Convert speed/dir

        """
        self.rawdata_df['temperature'] = coefA + coefB*self.rawdata_df['temp_engr'] + \
            + coefC*(self.rawdata_df['temp_engr']**2) + coefD*(self.rawdata_df['temp_engr']**3)

    def engr2sci_pres(self,coefA=0,coefB=0,coefC=0,equationType='low'):

        if equationType=='low':
           self.rawdata_df['pressure'] =(coefA+coefB*self.rawdata_df['press_engr']+coefC*(self.rawdata_df['press_engr']**2))/10-10

    def mag_dec_corr(self,lat,lonW,dep_date,apply_correction=True):
        """Calculate mag declinatin correction based on lat, lon (+ West) and date.

        Uses WMM_2020.COF - this model file updates every 5 years for current data.  Be sure to update this in future

        Args:
            lat (float): [description]
            lonW (float): [description]
            dep_date (datetime): [description]
            apply_correction (boolean): correct the u,v for mag dec.  False just reports back the correction angle.

        Returns:
            float: [description]
        """

        import ecofocipy.math.geomag.geomag.geomag as geomag
        import ecofocipy.math.geotools as geotools

        t = geomag.GeoMag()
        dec = t.GeoMag(lat,-1 * lonW,time=dep_date).dec

        (u,v) = geotools.rotate_coord(self.rawdata_df['u_curr_comp'],self.rawdata_df['v_curr_comp'],dec)

        self.rawdata_df['u_curr_comp'] = u
        self.rawdata_df['v_curr_comp'] = v

        return (self.rawdata_df,dec)

    def get_data(self):

        return (self.rawdata_df)

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

    @staticmethod
    def parse(filename=None, datetime_index=True):
        r"""
        Basic Method to open and read rcm text files
        """

        assert filename != None , 'Must provide a datafile'

        header = []

        with open(filename) as fobj:
            for k, line in enumerate(fobj.readlines()):
                header = header + [line]
                if "Record" in line:
                    headercount=k
                    break


        rawdata_df = pd.read_csv(filename, 
                        delimiter="\t", 
                        parse_dates=True, 
                        skiprows=headercount)
        rawdata_df["date_time"] = pd.to_datetime(rawdata_df["Time tag (Gmt)"], format="%d.%m.%Y %H:%M:%S")
        self.rawdata_df = rawdata_df

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time',"Time tag (Gmt)"],axis=1)        

        return (rawdata_df,header)

    def load(self,data):
        self.rawdata_df = data

    def mag_dec_corr(self,lat,lonW,dep_date,apply_correction=True):
        """Calculate mag declinatin correction based on lat, lon (+ West) and date.

        Uses WMM_2020.COF - this model file updates every 5 years for current data.  Be sure to update this in future

        Args:
            lat (float): [description]
            lonW (float): [description]
            dep_date (datetime): [description]
            apply_correction (boolean): correct the u,v for mag dec.  False just reports back the correction angle.

        Returns:
            float: [description]
        """

        import ecofocipy.math.geomag.geomag.geomag as geomag
        import ecofocipy.math.geotools as geotools

        t = geomag.GeoMag()
        dec = t.GeoMag(lat,-1 * lonW,time=dep_date).dec

        (u,v) = geotools.rotate_coord(self.rawdata_df['u_curr_comp'],self.rawdata_df['v_curr_comp'],dec)

        self.rawdata_df['u_curr_comp'] = u
        self.rawdata_df['v_curr_comp'] = v

        return (self.rawdata_df,dec)