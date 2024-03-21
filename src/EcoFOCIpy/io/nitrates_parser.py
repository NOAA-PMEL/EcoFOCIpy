# EcoFOCI
r"""
Contains a collection of nitrate equipment parsing.

These include:

* SUNA
* ISUS


"""
import pandas as pd


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
        self.data_frame = self.data_frame.resample('1H').median(numeric_only=True)

        return self.data_frame
