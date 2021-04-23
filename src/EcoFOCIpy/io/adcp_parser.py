# EcoFOCI
"""Contains a collection of ADCP equipment parsing.

These include:

* LR-ADCP
* Teledyne ADCP
* RCM ADCP


"""

import pandas as pd
import numpy as np

class adcp(object):
    """
    """
    def __init__(self,serialno=None,depdir=None):
        if depdir:
            self.depdir = depdir + serialno
        else:
            self.depdir = None

    def load_pg_file(self, pgfile_path=None, datetime_index=True):
        """load Pecent Good (PG) file
        The four Percent Good values represent (in order): 
            1) The percentage of good three beam solutions (one beam rejected); 
            2) The percentage of good transformations (error velocity threshold not exceeded); 
            3) The percentage of measurements where more than one beam was bad;
            4) The percentage of measurements with four beam solutions. <--- use this to qc data stream

        Args:
            pgfile_path (str, optional): full path to pg file. Defaults to ''.
        """
        if self.depdir:
            pgfile_path = self.depdir + '.PG'

        self.pg_df = pd.read_csv(pgfile_path,delimiter='\s+',header=None,names=['date','time','bin','pg3beam-good','pgtransf-good','pg1beam-bad','pg4beam-good'])
        self.pg_df["date_time"] = pd.to_datetime(self.pg_df.date+' '+self.pg_df.time,format="%y/%m/%d %H:%M:%S")
            
        if datetime_index:
            self.pg_df = self.pg_df.set_index(pd.DatetimeIndex(self.pg_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        return self.pg_df

    def load_ein_file(self, einfile_path=None, datetime_index=True):
        if self.depdir:
            einfile_path = self.depdir + '.EIN'

        self.ein_df = pd.read_csv(einfile_path,delimiter='\s+',header=None,names=['date','time','bin','agc1','agc2','agc3','agc4'])
        self.ein_df["date_time"] = pd.to_datetime(self.ein_df.date+' '+self.ein_df.time,format="%y/%m/%d %H:%M:%S")
            
        if datetime_index:
            self.ein_df = self.ein_df.set_index(pd.DatetimeIndex(self.ein_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        return self.ein_df

    def load_vel_file(self, velfile_path=None, datetime_index=True):
        if self.depdir:
            velfile_path = self.depdir + '.VEL'

        self.vel_df = pd.read_csv(velfile_path,delimiter='\s+',header=None,
                                    names=['date','time','bin','u_curr_comp','v_curr_comp','w_curr_comp','w_curr_comp_err'])
        self.vel_df["date_time"] = pd.to_datetime(self.vel_df.date+' '+self.vel_df.time,format="%y/%m/%d %H:%M:%S")
            
        if datetime_index:
            self.vel_df = self.vel_df.set_index(pd.DatetimeIndex(self.vel_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        return self.vel_df

    def load_scal_file(self, scalfile_path=None, datetime_index=True):
        if self.depdir:
            scalfile_path = self.depdir + '.SCA'

        self.scal_df = pd.read_csv(scalfile_path,delimiter='\s+',header=None,
                                    names=['date','time','unknown','temperature','heading','pitch','roll','heading_stdev','pitch_stdev','roll_stdev'])
        self.scal_df["date_time"] = pd.to_datetime(self.scal_df.date+' '+self.scal_df.time,format="%y/%m/%d %H:%M:%S")
            
        if datetime_index:
            self.scal_df = self.scal_df.set_index(pd.DatetimeIndex(self.scal_df['date_time'])).drop(['date_time','date','time'],axis=1)        

        return self.scal_df

    def load_rpt_file(self, rptfile_path=''):
        """[summary]

        Args:
            rptfile_path (str, optional): [description]. Defaults to ''.
            datetime_index (bool, optional): [description]. Defaults to True.

        Returns:
            [type]: [description]
        """
        if self.depdir:
            rptfile_path = self.depdir + '.RPT'

        adf = []
        self.setup = {}
        with open(rptfile_path) as fobj:
            for k, line in enumerate(fobj.readlines()):
                adf = adf + [line]
                if "Bin length" in line:
                    self.setup['bin_length'] = float(line.strip().split()[2])
                if "Distance" in line:
                    self.setup['distance'] = float(line.strip().split()[4])
                if "Number of bins" in line:
                    self.setup['numofbins'] = float(line.strip().split()[3])
        return (adf, self.setup)

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

        import EcoFOCIpy.math.geomag.geomag.geomag as geomag
        import EcoFOCIpy.math.geotools as geotools

        t = geomag.GeoMag()
        dec = t.GeoMag(lat,-1 * lonW,time=dep_date).dec

        (u,v) = geotools.rotate_coord(self.vel_df['u_curr_comp'],self.vel_df['v_curr_comp'],dec)

        self.vel_df['u_curr_comp'] = u
        self.vel_df['v_curr_comp'] = v

        return dec

    def bins2depth(self,depth_int,depth2firstbin,numofbins,inst_depth):
        """Convert bin count to verticle depth value given:
        distance to first bin (distance from head) and binwidth (distance between bins)

        Args:
            depth_int (float, optional): Spacing between bins. Defaults to None.
            depth_int (float, optional): Spacing between bins. Defaults to None.
        """
        start = inst_depth-depth2firstbin
        stop = start - numofbins*depth_int
        
        return np.arange(start,stop,-1*depth_int)