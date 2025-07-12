# EcoFOCI
r"""
Contains a collection of nitrate equipment parsing.

These include:

* SUNA
* ISUS


"""
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import re


# Satlantic Suna CSV
class Suna(object):
    r""" Satlantic SUNA
        Basic Method to open files.  Specific actions can be passed as kwargs for instruments

        Assumes SUNA csv output

    """
    def __init__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.data_frame = []

    def parse(self,filename=None):
        """
        Basic Method to open and read SUNA csv files.

        Parameters:
        ----------
        filename : str
            Path to the CSV file to be read.

        Returns:
        -------
        DataFrame
            The parsed data as a pandas DataFrame.
        """
        assert filename is not None, 'Must provide a datafile'

        # This is sloppy, assumes fixed format of columns
        rawdata_df = pd.read_csv(filename,
                                 header=None,
                                 parse_dates=True,
                                 index_col=1)

        rawdata_df.rename(columns={0:'Model/Serial',2:'Nitrate concentration, μM',
                   3:'Nitrogen in nitrate, mgN/L',
                   4:'Absorbance, 254 nm',5:'Absorbance, 350 nm',6:'Bromide trace, mg/L',
                   7:'Spectrum average', 8:'Dark value used for fit', 9:'Integration time factor',
                   266:'Internal temperature, °C', 267:'Spectrometer temperature, °C',
                   268:'Lamp temperature, °C', 269:'Cumulative lamp on-time, secs',
                   270:'Relative humidity, %', 271:'Main voltage, V',
                   272:'Lamp voltage, V', 273:'Internal voltage, V', 274:'Main current, mA',
                   275:'Fit aux 1', 276:'Fit aux 2', 277:'Fit base 1', 278:'Fit base 2',
                   279:'Fit RMSE'},inplace=True)

        # Set the index name
        rawdata_df.index.names = ['date_time']

        self.data_frame = rawdata_df

        return self.data_frame

    def plot_data(self, title="SUNA Data"):
        """
        Plot nitrate, spectral data, and Fit RMSE from the SUNA instrument for an initial check.

        Parameters:
        ----------
        title : str
            Title of the plot.
        """
        if self.data_frame.empty:
            raise ValueError("Data frame is empty. Please parse a file first.")

        # Plot nitrate data
        nitrate = self.data_frame['Nitrate concentration, μM']
        nitrate = nitrate.resample('1h').mean()

        # Plot Fit RMSE data
        fit_rmse = self.data_frame['Fit RMSE']

        # Plot spectral data
        spectra = self.data_frame.iloc[:, 10:266]
        wavelengths = [round(190 + (370-190)/255 * i, 2) for i in range(256)]
        spectra.columns = wavelengths
        spectra = spectra.resample('1h').mean()

        # Create subplots
        fig, axs = plt.subplots(3, 1, figsize=(11, 10), gridspec_kw={'height_ratios': [1, 1, 1.5]})

        # Nitrate subplot
        ax1 = axs[0]
        ax1.plot(nitrate.index, nitrate, color='C0')
        ax1.set(title='Nitrate Concentration', ylabel='Nitrate concentration (μM)')
        ax1.label_outer()  # Only show outer labels to avoid overlap

        # Fit RMSE subplot
        ax2 = axs[1]
        ax2.scatter(fit_rmse.index, fit_rmse, alpha=0.7)
        ax2.set(title='Fit RMSE', xlabel='Time', ylabel='Fit RMSE')
        ax2.label_outer()  # Only show outer labels to avoid overlap

        # Spectra subplot
        ax3 = axs[2]
        pcm = ax3.pcolormesh(spectra.index, spectra.columns, spectra.T, cmap=plt.cm.plasma)
        ax3.set(title='Spectral Data', xlabel='Time', ylabel='Wavelength (nm)',
                ylim=[200, 250])

        # Adjust layout manually to make room for the colorbar
        fig.subplots_adjust(right=0.85)
        cbar_ax = fig.add_axes([0.87, 0.10, 0.02, 0.3])
        fig.colorbar(pcm, cax=cbar_ax, label='Intensity')

        # Set the overall title and layout
        plt.suptitle(title, y=0.98)
        plt.show()
        
    def FilterSuna(self,rmse_cutoff=0.00025):
        """
        This method first applies a rmse_cutoff value specified as a keyword argument 
        (defaults to 0.00025).  It then remove entries with RMSE = 0. 
        In the end it resamples the data to hourly, and then takes the median 
        of the hour.
        """

        assert 'Fit RMSE' in self.data_frame.columns , 'Must provide a Fit RMSE column in data'
        
        self.data_frame = self.data_frame[(self.data_frame['Fit RMSE'] > 0) & (self.data_frame['Fit RMSE'] <= rmse_cutoff)]
        
        self.data_frame = self.data_frame.resample('1h').median(numeric_only=True)

        return self.data_frame


# Satlantic ISUS CSV
class Isus(object):
    """
    Satlantic ISUS nitrate sensor

    Methods:
    --------
    parse(filename)
        Load ISUS CSV file into a pandas DataFrame.

    plot_data(title)
        Quick-look plots for nitrate, RMS Error, and spectra.

    filter_isus(rmse_cutoff)
        Basic QC filter on RMS Error, then resamples to hourly median.
    """

    def __init__(self):
        self.data_frame = []

    def parse(self, filename=None):
        """
        Parse ISUS merged CSV file and build proper datetime index
        from YYYYDDD and HH.HHHHH. Drops the original columns after indexing.

        Parameters:
        ----------
        filename : str
            Path to the CSV file.

        Returns:
        -------
        DataFrame
        """
        assert filename is not None, "Must provide a data file"

        # Read raw file
        rawdata_df = pd.read_csv(filename)

        # Confirm required columns exist
        assert 'YYYYDDD' in rawdata_df.columns, "'YYYYDDD' column not found"
        assert 'HH.HHHHH' in rawdata_df.columns, "'HH.HHHHH' column not found"

        # Build datetime index
        yyyyddd = rawdata_df['YYYYDDD'].astype(str)
        fractional_hours = rawdata_df['HH.HHHHH'].astype(float)

        base_dates = pd.to_datetime(yyyyddd, format='%Y%j')
        datetimes = base_dates + pd.to_timedelta(fractional_hours, unit='h')

        rawdata_df.index = datetimes
        rawdata_df.index.name = 'date_time'

        # Drop original columns
        rawdata_df = rawdata_df.drop(columns=['YYYYDDD', 'HH.HHHHH'])

        self.data_frame = rawdata_df
        return self.data_frame


    def plot_data(self, title="ISUS Data"):
        """
        Quick plots for ISUS:
          - Nitrate concentration
          - RMS Error
          - Spectral data
        """
        import matplotlib.pyplot as plt
    
        if self.data_frame.empty:
            raise ValueError("Data frame is empty. Please parse a file first.")
    
        df = self.data_frame
    
        # 1. Smart drop of dark fiber
        df_no_dark = (
            df.groupby(pd.Grouper(freq='h'))
              .apply(lambda g: g.iloc[1:] if len(g) > 1 else g)
              .droplevel(0)
        )
    
        if df_no_dark.empty:
            print("[INFO] All data removed after dropping dark fiber readings.")
            return
    
        # 2. Basic data
        nitrate = df_no_dark['NO3_conc'].resample('1h').mean()
        fit_rmse = df_no_dark['RMS Error']
    
        # 3. Spectra: auto slice by presence of 'S/N'
        spectra_slice = (18, 274) if 'S/N' in df_no_dark.columns else (17, 273)
        spectra = df_no_dark.iloc[:, slice(*spectra_slice)]
    
        if spectra.empty:
            print("[INFO] No spectral data available after dropping darks.")
            return
    
        spectra = spectra.resample('1h').mean()
        if spectra.empty:
            print("[INFO] No spectral data available after resampling.")
            return
    
        # 4. Plot setup
        fig, axs = plt.subplots(
            3, 1, figsize=(11, 10),
            gridspec_kw={'height_ratios': [1, 1, 1.5]}
        )
    
        # 5. Nitrate plot
        axs[0].plot(nitrate.index, nitrate, color='C0')
        axs[0].set(title='Nitrate Concentration', ylabel='Nitrate (μM)')
        axs[0].label_outer()
    
        # 6. RMS Error plot
        axs[1].scatter(fit_rmse.index, fit_rmse, alpha=0.7)
        axs[1].set(title='RMS Error', xlabel='Time', ylabel='RMS Error')
        axs[1].label_outer()
    
        # 7. Spectral plot
        ax3 = axs[2]
        extent = [
            spectra.index[0].to_pydatetime(),
            spectra.index[-1].to_pydatetime(),
            float(spectra.columns[0]),
            float(spectra.columns[-1])
        ]
        im = ax3.imshow(spectra.to_numpy().T, 
                        aspect='auto', origin='lower', cmap=plt.cm.plasma, extent=extent)
        ax3.set(title='Spectral Data',
                xlabel='Time',
                ylabel='Wavelength (nm)',
                ylim=[200, 250])
        fig.autofmt_xdate()
    
        # 8. Colorbar
        fig.subplots_adjust(right=0.85)
        cbar_ax = fig.add_axes([0.87, 0.2, 0.02, 0.25])
        fig.colorbar(im, cax=cbar_ax, label='Intensity')
    
        plt.suptitle(title, y=0.98)
        plt.show()

    def FilterIsus(self, rmse_cutoff=0.003):
        """
        Filter ISUS data:
          - Keep rows with RMS Error > 0 and <= cutoff.
          - Resample to hourly median.

        Returns:
        -------
        DataFrame
        """
        assert 'RMS Error' in self.data_frame.columns, "Must have RMS Error column"
        df = self.data_frame

        # Drop dark fiber readings
        df_no_dark = df.groupby(pd.Grouper(freq='h')).apply(lambda g: g.iloc[1:])
        df_no_dark.index = df_no_dark.index.droplevel(0)        

        filtered_df = df_no_dark[(df_no_dark['RMS Error'] > 0) & (df_no_dark['RMS Error'] <= rmse_cutoff)]
        filtered_df = filtered_df.resample('1h').median(numeric_only=True)

        self.data_frame = filtered_df
        return self.data_frame


    
# Instrument files mapping with multiple calibration files
# TODO: have this be a configuration file that can be modified without changing code base
instrument_files = {
    'SUNA 1471': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_1471/2020/SNA1471B.cal'
    ],
    'SUNA 2341': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA-2341/2024/SNA2341C.CAL'
    ],
    'SUNA 1467': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_1467/SNA1467A.cal'
    ],
    'SUNA 1468': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_1468/SNA1468C.cal'
    ],
    'SUNA 1813': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_1813/2021/SNA1813B.cal'
    ],
    'SUNA 522': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_522/2014/Calibration%20files/SNA0522A.cal'
    ],
    'SUNA 598': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_598/2015/Calibration%20files/SNA0598A.cal', # 2015
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_598/2020/SNA0598F.cal' # 2020
    ],
    'SUNA 647': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_647/2015/calibration_files_647/SNA0647A.cal'
    ],
    'SUNA 648': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_648/2015/calibration_files_648/SNA0648B.cal', # 2015
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_648/2016/Calibration%20files/SNA0648C.cal' # 2016
    ],
    'SUNA 789': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_789/2016/SNA0789B.cal', # 2016
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_789/2021/SNA0789H.cal' # 2021
    ],
    'SUNA 796': [
        'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_796/2016/SNA0796A.cal'
    ],
    # Add more instruments and their calibration file URLs here
}

def get_calibration_file(instrument, data_year, user_provided_file=None):
    """
    Retrieve the appropriate calibration file for a specified instrument and data year.
    If the user provides a file, it is used instead of retrieving one from the online mapping.

    Parameters:
    ----------
    instrument : str
        The name of the instrument (e.g., 'SUNA 1471').
    data_year : int
        The year the data was collected.
    user_provided_file : str, optional
        Path to a user-provided calibration file.

    Returns:
    -------
    str
        The content of the calibration file.
    """
    # If the user provided a file, use it
    if user_provided_file:
        with open(user_provided_file, 'r') as file:
            return file.read()
    
    # Otherwise, retrieve the calibration file from the instrument mapping
    urls = instrument_files.get(instrument)
    if not urls:
        raise ValueError(f"Instrument '{instrument}' not found in the mapping.")
    
    # Extract the year from each URL and find the most appropriate calibration file
    cal_years = []
    default_url = None
    for url in urls:
        segments = url.split('/')
        year = None
        for segment in segments[-4:]:
            try:
                possible_year = int(segment)
                if 1900 <= possible_year <= datetime.now().year:
                    year = possible_year
                    break
            except ValueError:
                continue
        if year:
            cal_years.append((year, url))
        else:
            default_url = url
    
    if not cal_years:
        if default_url:
            selected_url = default_url
        else:
            raise ValueError(f"No suitable calibration file found for the instrument '{instrument}' and data year '{data_year}'.")
    else:
        cal_years.sort(reverse=True)
        selected_url = cal_years[0][1]
        for year, url in cal_years:
            if data_year >= year:
                selected_url = url
                break

    response = requests.get(selected_url)
    if response.status_code == 200:
        return response.text
    else:
        raise ValueError(f"Failed to retrieve file from {selected_url}")


def parse_no3_cal(calibration_content):
    """
    Parse the calibration content for NO3 sensors.

    Parameters:
    ----------
    calibration_content : str
        The content of the calibration file.

    Returns:
    -------
    ncal : dict
        A dictionary containing calibration constants and data.

    Notes:
    -----
    The calibration file contains header information and a data section.
    The header provides specific calibration constants while the data section includes
    Wavelengths, NO3, ESW, and Reference values.
    """
    # Initialize the calibration data structure
    ncal = {
        'WL': [],          # Wavelength array
        'ENO3': [],        # Extinction coefficients for nitrate at WL's
        'ESW': [],         # Extinction coefficients for seawater at WL's
        'Ref': [],         # Reference intensity through pure water at WL's
        'CalTemp': None,   # temperature the instrument was calibrated in the lab
        'WL_offset': 210,  # Adjustable Br wavelength offset (default = 210)
        'pixel_base': 1,   # Default is 1 (1-256), 0 (0-255)
        'DC_flag': 1,      # Default is 1 (can change later); 1 use DC in NO3 calc, 0 use SWDC in NO3 calc
        'pres_coef': 0.02  # Bromide extinction coefficient
    }

    # Split the content into lines
    lines = calibration_content.split('\n')

    # Parse header lines for calibration constants
    for line in lines:
        if line.startswith('H,'):
            if 'T_CAL' in line:
                ncal['CalTemp'] = extract_value_from_line(line)

    # Parse data lines starting with "E,"
    for line in lines:
        if line.startswith('E,'):
            columns = line.split(',')
            if len(columns) >= 6:
                # Replace '?' with NaN during parsing
                wl = float(columns[1])
                eno3 = float(columns[2]) if columns[2] != '?' else np.nan
                esw = float(columns[3]) if columns[3] != '?' else np.nan
                ref = float(columns[5]) if columns[5] != '?' else np.nan

                # Append values to the respective lists
                ncal['WL'].append(wl)
                ncal['ENO3'].append(eno3)
                ncal['ESW'].append(esw)
                ncal['Ref'].append(ref)

    return ncal

def extract_value_from_line(line):
    """
    Extract numerical value from a header line.

    Parameters:
    ----------
    line : str
        The header line containing the key-value pair.

    Returns:
    -------
    float
        The extracted numerical value.
    """
    # Split the line by space and extract the last element, then convert to float
    return float(line.split()[-1])


import numpy as np

def parse_isus_cal(calibration_content):
    """
    Parse the calibration content for ISUS sensors.

    Parameters:
    ----------
    calibration_content : str
        The content of the calibration file.

    Returns:
    -------
    ncal : dict
        A dictionary containing calibration constants and data.
    """
    # Initialize structure
    ncal = {
        'WL': [],          # Wavelength array
        'ENO3': [],        # Extinction coefficients for nitrate
        'ESW': [],         # Extinction coefficients for seawater
        'Ref': [],         # Reference intensity
        'CalTemp': None,   # Temperature the instrument was calibrated in the lab
        'WL_offset': 210,  # Adjustable Br wavelength offset (default = 210)
        'pixel_base': 1,   # Default is 1 (1-256), 0 (0-255)
        'DC_flag': 1,      # Default is 1 (can change later); 1 use DC in NO3 calc, 0 use SWDC in NO3 calc
        'pres_coef': 0.02  # Bromide extinction coefficient
    }
    
    lines = calibration_content.split('\n')

    for line in lines:
        if line.startswith('H,'):
            # Extract known header constants
            if 'T_CAL_SWA' in line:
                ncal['CalTemp'] = extract_isus_value_from_line(line)
            
        elif line.startswith('E,'):
            columns = line.split(',')
            if len(columns) >= 6:
                wl = float(columns[1])
                eno3 = try_parse_float(columns[2])
                esw = try_parse_float(columns[3])
                ref = try_parse_float(columns[5])

                ncal['WL'].append(wl)
                ncal['ENO3'].append(eno3)
                ncal['ESW'].append(esw)
                ncal['Ref'].append(ref)

    return ncal

def extract_isus_value_from_line(line):
    """
    Extract the first numeric float from an ISUS header line,
    even if it's attached to text.
    Example: 'H,T_CAL_SWA 20,,,'  ->  20.0
    """
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", line)
    if matches:
        return float(matches[0])
    else:
        return None

def try_parse_float(value):
    """
    Handle '?' or missing values in the E lines.
    """
    try:
        return float(value)
    except ValueError:
        return np.nan
