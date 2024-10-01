# EcoFOCI
"""
Apply corrections to the nitrate data.

These include:

* SUNA
* ISUS (not developed yet)

"""
import numpy as np
import pandas as pd

def calc_nitrate_concentration(suna_wop_filtered, s16_interpolated, ncal, WL_offset=210, pres_coef=0.026, sat_value=64500):
    """
    Calculate nitrate concentration from SUNA data with necessary corrections. 
    This includes temperature correction, pressure correction, and dark current handling.
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
        Calibration data including wavelength, nitrate extinction, seawater extinction, 
        and reference spectrum.
    WL_offset : float
        Adjustable Br wavelength offset (default = 210).
    pres_coef : float
        Bromide extinction coefficient (default = 0.026).
    sat_value : int
        Pixel intensity saturation limit count (default = 64500).
        
    Returns:
    -------
    no3_concentration : DataFrame
        Calculated nitrate concentration.
    WL_UV : ndarray
        Wavelength array corresponding to UV intensity data.
    E_N_interp : ndarray
        Interpolated nitrate extinction coefficient.
    E_S_interp : ndarray
        Interpolated seawater extinction coefficient.
    ESW_in_situ : ndarray
        In situ seawater extinction coefficient after temperature correction.
    ESW_in_situ_p : ndarray
        In situ seawater extinction coefficient after pressure correction.
    ABS_SW : ndarray
        Total absorbance from UV intensity.
    ABS_Br_tcor : ndarray
        Bromide-corrected absorbance.
    ABS_cor : ndarray
        Nitrate and baseline absorbance after bromide correction.
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
    E_ref = np.array(ncal['Ref'])

    # Interpolate ncal coefficients to match the UV intensity wavelengths (WL_UV)
    E_N_interp = np.interp(WL_UV, WLcal, E_N)
    E_S_interp = np.interp(WL_UV, WLcal, E_S)
    E_ref_interp = np.interp(WL_UV, WLcal, E_ref)


    # ************************************************************************
    # Choose fit window. The Argo default processing uses a default window of >=217 & <=240.
    # But the Plant2023 paper indicates that cofficients of determination for the regressions 
    # at each wavelength exhibit high correlations between 210 to 230 nm. 
    # Here we choose to use 217 to 240 nm for data processing and this window can be 
    # adjusted later as needed. 
    # ************************************************************************
    
    fit_window_UV   = (WL_UV >= 217) & (WL_UV <= 240)

    # Apply the fit window mask to the interpolated ncal coefficients and UV data
    WL_UV = WL_UV[fit_window_UV]
    spec_UV_INTEN = spec_UV_INTEN[:, fit_window_UV]
    E_N_interp = E_N_interp[fit_window_UV]
    E_S_interp = E_S_interp[fit_window_UV]
    E_ref_interp = E_ref_interp[fit_window_UV]

    # ************************************************************************
    # Handle saturation and subtract dark current values
    # ************************************************************************    

    # Handle saturation (set saturated pixels to NaN)
    tPIX_SAT = spec_UV_INTEN > sat_value
    if np.sum(tPIX_SAT) > 0:
        print('WARNING: Saturated sample pixel intensities detected in profile')
        print('Saturated values will be excluded. Nitrate estimates may be compromised')
        spec_UV_INTEN = np.where(tPIX_SAT, np.nan, spec_UV_INTEN)
    
    # Subtract dark current and set values <= 0 to NaN
    dark_current = suna_wop_filtered['Dark value used for fit'].values[:, np.newaxis]  # reshape for broadcasting
    spec_UV_INTEN = spec_UV_INTEN - dark_current
    spec_UV_INTEN = np.where(spec_UV_INTEN > 0, spec_UV_INTEN, np.nan)

    # ************************************************************************
    # Temperature and pressure corrections
    # ************************************************************************    

    
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
    ESW_in_situ_p = ESW_in_situ * pres_term  # Shape: (spec_SDN, n_wavelength)

    # ************************************************************************
    # Calculate absorbance
    # ************************************************************************    
    
    # Compute the total absorbance (ABS_SW) from the UV intensity and dark-corrected reference spectrum
    # Correct E_ref by subtracting the dark values
    E_ref_dark_corrected = E_ref_interp - dark_current
    ABS_SW = -np.log10(spec_UV_INTEN / E_ref_dark_corrected)  

    # Compute the in situ bromide absorbances based on salinity and ESW_in_situ
    ABS_Br_tcor = ESW_in_situ * spec_S[:, np.newaxis] 
        
    # Subtract bromide absorbance from the total absorbance to get nitrate + baseline absorbance
    ABS_cor = ABS_SW - ABS_Br_tcor 
    
    # return WL_UV, E_N_interp, E_S_interp, ESW_in_situ, ESW_in_situ_p, ABS_SW, ABS_Br_tcor, ABS_cor, spec_UV_INTEN, E_ref_dark_corrected

    # ************************************************************************
    # CALCULATE THE NITRATE CONCENTRATION, BASELINE SLOPE AND INTERCEPT OF THE
    # BASELINE ABSORBANCE. Following the example here: 
    # https://github.com/SOCCOM-BGCArgo/ARGO_PROCESSING/blob/master/MFILES/FLOATS/calc_FLOAT_NO3.m
    # ************************************************************************

    # Prepare fit matrix (M) and pseudo-inverse (M_INV)
    Ones = np.ones_like(E_N_interp)
    M = np.column_stack([E_N_interp, Ones / 100, WL_UV / 1000])  # Wavelength x 3
    M_INV = np.linalg.pinv(M)

    # Perform the nitrate concentration calculation
    NO3 = calculate_no3_concentration(ABS_cor, E_N_interp, WL_UV, M, M_INV)

    # Return the result as a DataFrame
    no3_concentration = pd.DataFrame(data=NO3, index=spec_SDN, 
                                     columns=['Nitrate concentration (μM)', 'Baseline Intercept', 
                                              'Baseline Slope', 'RMS Error', 'Wavelength @ 240nm', 
                                              'Absorbance @ 240nm'])
    
    return no3_concentration, WL_UV, E_N_interp, E_S_interp, ESW_in_situ, ESW_in_situ_p, ABS_SW, ABS_Br_tcor, ABS_cor, spec_UV_INTEN, E_ref_dark_corrected



# Calculate nitrate concentration, baseline slope, and intercept
def calculate_no3_concentration(ABS_cor, E_N_interp, WL_UV, M, M_INV):
    """
    Performs the nitrate concentration, baseline intercept, and slope calculations for each sample.
    """
    rows = ABS_cor.shape[0]
    NO3 = np.full((rows, 6), np.nan)  # Preallocate NO3 array (samples x 6 metrics)

    for i in range(rows):
        tg = np.isfinite(ABS_cor[i, :])  # Identify valid data points
        m_inv = np.linalg.pinv(M[tg, :]) if np.sum(tg) > 0 else M_INV

        # Fit and calculate NO3 concentration, intercept, slope
        NO3[i, :3] = m_inv @ ABS_cor[i, tg] if np.sum(tg) > 0 else [np.nan, np.nan, np.nan]
        NO3[i, 1] /= 100  # Correct baseline intercept
        NO3[i, 2] /= 1000  # Correct baseline slope

        # Calculate absorbance and residuals
        ABS_BL = WL_UV * NO3[i, 2] + NO3[i, 1]
        ABS_NO3 = ABS_cor[i, :] - ABS_BL
        ABS_NO3_EXP = E_N_interp * NO3[i, 0]
        FIT_DIF = ABS_cor[i, :] - ABS_BL - ABS_NO3_EXP

        # Calculate RMS error, but only if there are valid points
        if np.sum(tg) > 0:
            RMS_ERROR = np.sqrt(np.sum(FIT_DIF[tg] ** 2) / np.sum(tg))
        else:
            RMS_ERROR = np.nan  # Assign NaN if no valid points

        # Store RMS error and absorbance near 240 nm
        ind_240 = np.argmin(np.abs(WL_UV - 240))
        ABS_240 = [WL_UV[ind_240], ABS_cor[i, ind_240]]
        NO3[i, 3:] = [RMS_ERROR, *ABS_240]

    return NO3
