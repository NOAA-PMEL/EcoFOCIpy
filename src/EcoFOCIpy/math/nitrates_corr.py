# EcoFOCI
"""
Apply corrections to the nitrate data.

These include:

* SUNA
* ISUS (not developed yet)

"""
import numpy as np
import pandas as pd

def calc_float_no3(suna_wop_filtered, s16_interpolated, ncal, WL_offset=210, pixel_base=1, DC_flag=1, pres_coef=0.02):
    """
    Calculate nitrate concentration from SUNA data with necessary corrections.

    Parameters:
    ----------
    suna_wop_filtered : DataFrame
        Filtered SUNA data.
    s16_interpolated : DataFrame
        Interpolated SBE-16 data at the same location.
    ncal : dict
        Calibration data.
    WL_offset : float
        Adjustable Br wavelength offset (default = 210).
    pixel_base : int
        Default is 1 (1-256), 0 (0-255).
    DC_flag : int
        1 to use DC in NO3 calc, 0 to use SWDC in NO3 calc (default = 1).
    pres_coef : float
        Bromide extinction coefficient (default = 0.02).

    Returns:
    -------
    no3_concentration : DataFrame
        Calculated nitrate concentration.
    """

    # Extract variables from dataframes
    spec_SDN = suna_wop_filtered.index
    spec_UV_INTEN = suna_wop_filtered.iloc[:, 8:264].values
    spec_T = s16_interpolated['temperature (degree_C)'].values
    spec_S = s16_interpolated['salinity (PSU)'].values
    spec_P = s16_interpolated['Water_Depth (dbar)'].values

    # Calibration coefficients
    Tcal = ncal['CalTemp']
    E_N = np.array(ncal['ENO3'])
    E_S = np.array(ncal['ESW'])
    E_ref = np.array(ncal['Ref'])
    
    # Create list with wavelengths
    wavelengths = [round(190 + 0.7 * i, 2) for i in range(256)]
    
    # Adjust wavelengths
    wavelengths = np.array(wavelengths) + WL_offset

    # Temperature correction coefficients
    Tcorr_coef  = [1.27353e-07, -7.56395e-06, 2.91898e-05, 1.67660e-03, 1.46380e-02]
    Tcorr = np.polyval(Tcorr_coef, (wavelengths - WL_offset)) * (spec_T - Tcal)
    
    # Correct for temperature difference
    E_N_corr = E_N * np.exp(Tcorr)
    ESW_in_situ = E_S * np.exp(Tcorr)

    # Calculate absorbance
    absorbance = -np.log10(spec_UV_INTEN / np.mean(spec_UV_INTEN, axis=0))

    # Calculate nitrate concentration
    NO3 = (absorbance @ E_N_corr) / (E_ref @ E_N_corr) - pres_coef * spec_S * spec_P / 1000

    # Create a DataFrame for nitrate concentration
    no3_concentration = pd.DataFrame(data=NO3, index=spec_SDN, columns=['Nitrate concentration (μM)'])

    return no3_concentration