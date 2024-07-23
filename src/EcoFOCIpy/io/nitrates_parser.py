# EcoFOCI
r"""
Contains a collection of nitrate equipment parsing.

These include:

* SUNA
* ISUS


"""
import pandas as pd
import requests


# Satlantic Suna CSV
class Suna(object):
    r""" Satlantic SUNA
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        Assumes SUNA csv output

    """
    def __init__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.data_frame = []

    def parse(self,filename=None):
        r"""
        Basic Method to open and read suna csv files

        """
        assert filename is not None , 'Must provide a datafile'

        ### This is sloppy, assumes fixed format of columns
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

        rawdata_df.index.names = ['date_time']

        self.data_frame = rawdata_df

        return self.data_frame

    def FilterSuna(self,rmse_cutoff=0.00025):
        """
        This method first applies a rmse_cutoff value specified as a keyword argument 
        (defaults to 0.00025).  It then resamples the data to hourly, and then takes the median 
        of the hour
        """

        assert 'Fit RMSE' in self.data_frame.columns , 'Must provide a Fit RMSE column in data'

        self.data_frame = self.data_frame[self.data_frame['Fit RMSE'] <= rmse_cutoff]
        self.data_frame = self.data_frame.resample('1h').median(numeric_only=True)

        return self.data_frame
    


    
    
# Instrument files mapping
instrument_files = {
    'SUNA 1471': 'https://raw.githubusercontent.com/NOAA-PMEL/EcoFOCI_FieldOps_Documentation/master/CalibrationsByVendor/Satlantic/SUNA_1471/2020/SNA1471B.cal',
    # Add more instruments and their paths here
}

def get_calibration_file(instrument):
    """
    Retrieve the calibration file for a specified instrument.

    Parameters:
    ----------
    instrument : str
        The name of the instrument (e.g., 'SUNA 1471').

    Returns:
    -------
    str
        The content of the calibration file.
    """
    url = instrument_files.get(instrument)
    if url:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise ValueError(f"Failed to retrieve file from {url}")
    else:
        raise ValueError(f"Instrument '{instrument}' not found in the mapping.")

def parse_no3_cal(calibration_content):
    """
    Parse the calibration content for NO3 sensors.

    Parameters:
    ----------
    calibration_content : str
        The content of the calibration file.

    Returns:
    -------
    dict
        A dictionary containing calibration constants and data.

    Notes:
    -----
    The calibration file contains header information and a data section.
    The header provides specific calibration constants while the data section includes
    Wavelengths, NO3, ESW, and Reference values.
    """
    # Initialize the calibration data structure
    ncal = {
        'WL': [],
        'ENO3': [],
        'ESW': [],
        'Ref': [],
        'CalTemp': None,
        'WL_offset': 210,  # Adjustable Br wavelength offset (default = 210)
        'pixel_base': 1,  # Default is 1 (1-256), 0 (0-255)
        'DC_flag': 1,  # Default is 1 (can change later); 1 use DC in NO3 calc, 0 use SWDC in NO3 calc
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
                # Ignore the first column and parse the rest. 
                # The ’TSWA’ column is Satlantic proprietary, which is not used.
                ncal['WL'].append(float(columns[1]))
                ncal['ENO3'].append(float(columns[2]))
                ncal['ESW'].append(float(columns[3]))
                ncal['Ref'].append(float(columns[5]))

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
                