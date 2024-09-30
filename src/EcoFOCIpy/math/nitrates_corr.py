# EcoFOCI
"""
Apply corrections to the nitrate data.

These include:

* SUNA
* ISUS (not developed yet)

"""
import numpy as np
import pandas as pd

def calc_float_no3(suna_wop_filtered, s16_interpolated, ncal, WL_offset=210, pixel_base=1, DC_flag=1, pres_coef=0.026):
    """
    Calculate nitrate concentration from SUNA data with necessary corrections. 
    Methods follow Plant et al. (2023): Updated temperature correction for computing seawater nitrate 
    with in situ ultraviolet spectrophotometer and submersible ultraviolet nitrate analyzer nitrate sensors. 
    Limnology and Oceanography: Methods.

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
    spec_UV_INTEN = suna_wop_filtered.iloc[:, 8:264].values # This is the UV intensity data
    WL_UV = suna_wop_filtered.columns[8:264].astype(float) # Extract the wavelengths from the column names 
    spec_T = s16_interpolated['temperature (degree_C)'].values 
    spec_S = s16_interpolated['salinity (PSU)'].values
    spec_P = s16_interpolated['Water_Depth (dbar)'].values
    
    # Calibration coefficients
    Tcal = ncal['CalTemp']
    WLcal = np.array(ncal['WL'])
    E_N = np.array(ncal['ENO3'])
    E_S = np.array(ncal['ESW'])
    # E_ref = np.array(ncal['Ref'])

    # Interpolate ncal coefficients to match the UV intensity wavelengths (WL_UV)
    E_N_interp = np.interp(WL_UV, WLcal, E_N)
    E_S_interp = np.interp(WL_UV, WLcal, E_S)
    # E_ref_interp = np.interp(WL_UV, WLcal, E_ref)

    # Choose fit window. The Argo default processing uses a default window of >=217 & <=240.
    # But the Plant2023 paper indicates that cofficients of determination for the regressions 
    # at each wavelength exhibit high correlations between 210 to 230 nm. 
    # Here we choose to use ** 210 to 240 nm ** for data processing and this window can be 
    # adjusted later as needed. 
    fit_window_UV   = (WL_UV >= 210) & (WL_UV <= 240)

    # Apply the fit window mask to the interpolated ncal coefficients and UV data
    WL_UV = WL_UV[fit_window_UV]
    spec_UV_INTEN = spec_UV_INTEN[:, fit_window_UV]
    E_N_interp = E_N_interp[fit_window_UV]
    E_S_interp = E_S_interp[fit_window_UV]
    # E_ref_interp = E_ref_interp[fit_window_UV]
    
    # Temperature correction coefficients (Eq. 6)
    Tcorr_coef  = [1.27353e-07, -7.56395e-06, 2.91898e-05, 1.67660e-03, 1.46380e-02]
    f_lambda    = np.polyval(Tcorr_coef, (WL_UV - WL_offset))

    # Calculate the temperature correction for each time step and wavelength
    T_diff = (spec_T - Tcal)[:, np.newaxis]
    Tcorr = f_lambda * T_diff
    
    # Correct for temperature difference (Eq. 8)
    ESW_in_situ = E_S_interp * np.exp(Tcorr)

    # Pressure correction term (Eq. 9)
    pres_term = (1 - spec_P[:, np.newaxis] / 1000 * pres_coef)  # Shape: (spec_SDN, 1)
    
    # Apply pressure correction to ESW_in_situ (element-wise multiplication)
    ESW_in_situ_p = ESW_in_situ * pres_term  # Shape: (spec_SDN, wavelength)

    # # Calculate absorbance
    # absorbance = -np.log10(spec_UV_INTEN / np.mean(spec_UV_INTEN, axis=0))
    
    return WL_UV, E_N_interp, E_S_interp, ESW_in_situ, ESW_in_situ_p, spec_UV_INTEN
    
    

    # # Calculate nitrate concentration
    # NO3 = (absorbance @ E_N_corr) / (E_ref @ E_N_corr) - pres_coef * spec_S * spec_P / 1000

    # # Create a DataFrame for nitrate concentration
    # no3_concentration = pd.DataFrame(data=NO3, index=spec_SDN, columns=['Nitrate concentration (μM)'])

    # return no3_concentration