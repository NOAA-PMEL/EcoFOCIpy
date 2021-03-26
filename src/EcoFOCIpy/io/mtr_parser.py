"""Contains a collection of MTR equipment parsing.

These include:

* Version 3/4 (old version) [ ]
* Version 5 (MTRduino) [x]

"""
import pandas as pd

class mtrduino(object):
    r""" MicroTemperature Recorders (MTR) - 5k / MTRduino generation
    Collection of static methods to define MTR processing and conversion

    It is assumed the data passed here is preliminarily processed and has calibration
    functions already applied

    ToDO:  Allow raw data to be passed"""

    @staticmethod
    def parse(filename=None, datetime_index=True, **kwargs):
        r"""
        Basic Method to open and read mtrduino raw converted csv files
            
            kwargs:
                round_10min_interval - force small deviations to 10min intervals.  Actually rounds all so it
                    is user responisbility to make sure values are representative first.

        """
        assert filename != None , 'Must provide a datafile'

        rawdata = pd.read_csv(
            filename, delimiter=",", parse_dates=["date_time"]
        )

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time'],axis=1)

        #previous algorithms rounded to 10min
        ## all time manipulation should either be outside the instrument methods
        ##  or optional via a method call... maybe not a flag like here??
        if kwargs["round_10min_interval"]:
            rawdata.index = rawdata.index.round("10min", inplace=True)

        return rawdata_df
