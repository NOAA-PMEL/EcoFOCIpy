# EcoFOCI
"""Contains a collection of ADCP equipment parsing.

These include:

* LR-ADCP
* Teledyne ADCP
* RCM ADCP

2025: Use Gemini to enhance and improve code rebase

"""

import numpy as np
import pandas as pd

class adcp(object):
    """
    """
    def __init__(self,serialno=None,depdir=None):
        if depdir:
            self.depdir = depdir + serialno
        else:
            self.depdir = None

    def _load_generic_file(self, file_path_arg, default_extension, names_list, datetime_index=True):
        """
        Helper method to load common ADCP data files.

        Args:
            file_path_arg (str, optional): full path to the file. If None, self.depdir + default_extension is used.
            default_extension (str): The file extension (e.g., '.PG', '.VEL').
            names_list (list): List of column names for the DataFrame.
            datetime_index (bool, optional): If True, sets a datetime index. Defaults to True.

        Returns:
            pd.DataFrame: Loaded and processed DataFrame.
        """
        file_to_load = file_path_arg
        if not file_to_load and self.depdir:
            file_to_load = self.depdir + default_extension
        elif not file_to_load and not self.depdir:
            raise ValueError(f"No file path provided and self.depdir is not set for {default_extension} file.")

        try:
            df = pd.read_csv(file_to_load, delimiter=r'\s+', header=None, names=names_list)
            df["date_time"] = pd.to_datetime(df.date + ' ' + df.time, format="%y/%m/%d %H:%M:%S")

            if datetime_index:
                df = df.set_index(pd.DatetimeIndex(df['date_time'])).drop(['date_time', 'date', 'time'], axis=1)
            return df
        except FileNotFoundError:
            print(f"Error: File not found at {file_to_load}")
            return None
        except Exception as e:
            print(f"Error loading {file_to_load}: {e}")
            return None
        
    def load_pg_file(self, pgfile_path : str = None, datetime_index=True):
        """load Pecent Good (PG) file
        The four Percent Good values represent (in order):
            1) The percentage of good three beam solutions (one beam rejected);
            2) The percentage of good transformations (error velocity threshold not exceeded);
            3) The percentage of measurements where more than one beam was bad;
            4) The percentage of measurements with four beam solutions. <--- use this to qc data stream

        Args:
            pgfile_path (str, optional): full path to pg file. Defaults to None.
        """
        names = ['date', 'time', 'bin', 'pg3beam-good', 'pgtransf-good', 'pg1beam-bad', 'pg4beam-good']
        self.pg_df = self._load_generic_file(pgfile_path, '.PG', names, datetime_index)
        return self.pg_df

    def load_ein_file(self, einfile_path=None, datetime_index=True):
        names = ['date', 'time', 'bin', 'agc1', 'agc2', 'agc3', 'agc4']
        self.ein_df = self._load_generic_file(einfile_path, '.EIN', names, datetime_index)
        return self.ein_df

    def load_vel_file(self, velfile_path=None, datetime_index=True):
        names = ['date', 'time', 'bin', 'u_curr_comp', 'v_curr_comp', 'w_curr_comp', 'w_curr_comp_err']
        self.vel_df = self._load_generic_file(velfile_path, '.VEL', names, datetime_index)
        return self.vel_df

    def load_scal_file(self, scalfile_path=None, datetime_index=True):
        names = ['date', 'time', 'unknown', 'temperature', 'heading', 'pitch', 'roll', 'heading_stdev', 'pitch_stdev', 'roll_stdev']
        self.scal_df = self._load_generic_file(scalfile_path, '.SCA', names, datetime_index)
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
