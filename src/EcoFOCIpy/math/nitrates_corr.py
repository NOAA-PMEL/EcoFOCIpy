# EcoFOCI
"""
Apply corrections to the nitrate data.

These include:

* SUNA
* ISUS (not developed yet)

"""
import numpy as np
import pandas as pd

def calc_nitrate_concentration(suna_wop_filtered, s16_interpolated, ncal, WL_offset=210, pres_coef=0.026):
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
    E_ref = np.array(ncal['Ref'])

    # Interpolate ncal coefficients to match the UV intensity wavelengths (WL_UV)
    E_N_interp = np.interp(WL_UV, WLcal, E_N)
    E_S_interp = np.interp(WL_UV, WLcal, E_S)
    E_ref_interp = np.interp(WL_UV, WLcal, E_ref)

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
    E_ref_interp = E_ref_interp[fit_window_UV]
    
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

    # Compute the total absorbance (ABS_SW) from the UV intensity and interpolated reference spectrum
    ABS_SW = -np.log10(spec_UV_INTEN / E_ref_interp)  

    # Compute the in situ bromide absorbances based on salinity and ESW_in_situ
    ABS_Br_tcor = ESW_in_situ * spec_S[:, np.newaxis] 
        
    # Subtract bromide absorbance from the total absorbance to get nitrate + baseline absorbance
    ABS_cor = ABS_SW - ABS_Br_tcor 


    # ************************************************************************
    # CALCULATE THE NITRATE CONCENTRATION, BASELINE SLOPE AND INTERCEPT OF THE
    # BASELINE ABSORBANCE. Following the example here: 
    # https://github.com/SOCCOM-BGCArgo/ARGO_PROCESSING/blob/master/MFILES/FLOATS/calc_FLOAT_NO3.m
    # ************************************************************************

    # Prepare the fit matrix (M)
    Ones = np.ones_like(E_N_interp)
    M = np.column_stack([E_N_interp, Ones/100, WL_UV/1000])  # Shape: (n_wavelengths, 3)
    M_INV = np.linalg.pinv(M)  # Pseudo-inverse of M

    # Preallocate NO3 array for storing results (3 columns for NO3 concentration, intercept, and slope)
    rows = ABS_cor.shape[0]
    NO3 = np.full((rows, 6), np.nan)  # #samples x (3 fit parameters + 3 QC metrics)

    # Iterate over each sample
    for i in range(rows):
        tg = np.isfinite(ABS_cor[i, :])  # Mask for valid (non-saturated) intensities
        
        if np.sum(tg) > 0:
            m_inv = np.linalg.pinv(M[tg, :])  # Subset M for non-saturated wavelengths
        else:
            m_inv = M_INV
        
        # Solve for NO3 concentration, baseline intercept, and slope
        NO3[i, :3] = m_inv @ ABS_cor[i, tg]  # Fit to get NO3, intercept, slope
        NO3[i, 1] /= 100  # Baseline intercept correction
        NO3[i, 2] /= 1000  # Baseline slope correction

        # Calculate baseline absorbance and nitrate absorbance
        ABS_BL = WL_UV * NO3[i, 2] + NO3[i, 1]
        ABS_NO3 = ABS_cor[i, :] - ABS_BL

        # Calculate expected nitrate absorbance from extinction coefficient
        ABS_NO3_EXP = E_N_interp * NO3[i, 0]

        # Calculate residuals and RMS error
        FIT_DIF = ABS_cor[i, :] - ABS_BL - ABS_NO3_EXP
        FIT_DIF_tfit = FIT_DIF[tg]
        RMS_ERROR = np.sqrt(np.sum(FIT_DIF_tfit ** 2) / np.sum(tg))

        # Find absorbance near 240 nm
        ind_240 = np.argmin(np.abs(WL_UV - 240))
        ABS_240 = [WL_UV[ind_240], ABS_cor[i, ind_240]]

        # Store RMS error and absorbance at ~240 nm
        NO3[i, 3:] = [RMS_ERROR, *ABS_240]

    # Return results in a DataFrame
    no3_concentration = pd.DataFrame(data=NO3, index=spec_SDN, columns=['Nitrate concentration (μM)', 'Baseline Intercept', 'Baseline Slope', 'RMS Error', 'Wavelength @ 240nm', 'Absorbance @ 240nm'])

    return no3_concentration


    return WL_UV, E_N_interp, E_S_interp, ESW_in_situ, ESW_in_situ_p, ABS_SW, ABS_Br_tcor, ABS_cor
    
    

    # # Calculate nitrate concentration
    # NO3 = (absorbance @ E_N_corr) / (E_ref @ E_N_corr) - pres_coef * spec_S * spec_P / 1000

    # # Create a DataFrame for nitrate concentration
    # no3_concentration = pd.DataFrame(data=NO3, index=spec_SDN, columns=['Nitrate concentration (μM)'])

    # return no3_concentration