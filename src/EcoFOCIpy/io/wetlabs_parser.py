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

class ecoflsb(object):
    r""" Wetlabs EcoFLS(B) - single channel fluorometer (B-battery pack)

    """

    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read fls(b) cnv files

        """

        header = []
        var_names = {}
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

    def engr2sci(self,cal_coef=[]):
        """convert counts to quantity using wetlabs coefficients"""
        pass

    def time_correction(self,offset=None):
        """ apply a time offset in seconds"""
        pass