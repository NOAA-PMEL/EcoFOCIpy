# EcoFOCI
"""
Apply corrections to the nitrate data.

These include:

* SUNA
* ISUS

"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def calc_nitrate_concentration(nitrate_data_filtered, s16_interpolated, ncal, inst_shortname='suna', WL_offset=210, pres_coef=0.026, sat_value=64500):
    """
    Calculate nitrate concentration from SUNA/ISUS data with necessary corrections. 
    This includes temperature correction, pressure correction, and dark current handling.
    Methods follow Plant et al. (2023): Updated temperature correction for computing seawater nitrate 
    with in situ ultraviolet spectrophotometer and submersible ultraviolet nitrate analyzer nitrate sensors. 
    Limnology and Oceanography: Methods.

    Parameters:
    ----------
    nitrate_data_filtered : DataFrame
        Filtered SUNA data.
    s16_interpolated : DataFrame
        Interpolated SBE-16 data at the same location.
    ncal : dict
        Calibration data including wavelength, nitrate extinction, seawater extinction, 
        and reference spectrum.
    inst_shortname : str, optional
        Short name for the instrument type ('suna' or 'isus').
        Determines which dark value column and UV spectral range to use.
        Defaults to 'suna'.        
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
    WL : ndarray
        Wavelength array corresponding to UV intensity data.
    E_N : ndarray
        Interpolated nitrate extinction coefficient.
    E_S : ndarray
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
    spec_UV_INTEN : ndarray
        Saturation filted, dark-corrected spectrum
    """

    # Extract variables from dataframes
    spec_SDN = nitrate_data_filtered.index
    spec_T = s16_interpolated['temperature (degree_C)'].values 
    spec_S = s16_interpolated['salinity (PSU)'].values
    spec_P = s16_interpolated['Water_Depth (dbar)'].values

    # Calibration coefficients
    Tcal = ncal['CalTemp']
    WL = np.array(ncal['WL'])
    E_N = np.array(ncal['ENO3'])
    E_S = np.array(ncal['ESW'])
    E_ref = np.array(ncal['Ref'])

    # === Instrument-specific parameters ===
    if inst_shortname.lower() == 'suna':
        dark_col = 'Dark value used for fit'
        spec_UV_INTEN = nitrate_data_filtered.iloc[:, 8:264].values
    
    elif inst_shortname.lower() == 'isus':
        dark_col = 'Sea-Water Dark Calculation'
        spec_UV_INTEN = nitrate_data_filtered.iloc[:, 17:273].values
    
    else:
        raise ValueError("inst_shortname must be 'suna' or 'isus'.")    

    # ************************************************************************
    # Choose fit window. The Argo default processing uses a default window of >=217 & <=240.
    # But the Plant2023 paper indicates that cofficients of determination for the regressions 
    # at each wavelength exhibit high correlations between 210 to 230 nm. 
    # Here we choose to use 217 to 240 nm for data processing and this window can be 
    # adjusted later as needed. 
    # ************************************************************************
    
    fit_window  = (WL >= 217) & (WL <= 240)

    # Apply the fit window mask to the ncal coefficients and UV data
    WL = WL[fit_window]
    E_N = E_N[fit_window]
    E_S = E_S[fit_window]
    E_ref = E_ref[fit_window]
    spec_UV_INTEN = spec_UV_INTEN[:, fit_window]

    
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
    # Currently use spectral mean dark values. Consider using dark values for individual wavelengths in the future.
    dark_current = nitrate_data_filtered[dark_col].values[:, np.newaxis]  # reshape for broadcasting
    spec_UV_INTEN = spec_UV_INTEN - dark_current
    spec_UV_INTEN = np.where(spec_UV_INTEN > 0, spec_UV_INTEN, np.nan)

    
    # ************************************************************************
    # Temperature and pressure corrections for E_S
    # ************************************************************************    
    
    # Temperature correction coefficients (Eq. 6)
    Tcorr_coef  = [1.27353e-07, -7.56395e-06, 2.91898e-05, 1.67660e-03, 1.46380e-02]
    f_lambda    = np.polyval(Tcorr_coef, (WL - WL_offset))

    # Calculate the temperature correction for each time step and wavelength
    T_diff = (spec_T - Tcal)[:, np.newaxis]
    Tcorr = f_lambda * T_diff
    
    # Correct for temperature difference (Eq. 8)
    ESW_in_situ = E_S * np.exp(Tcorr)

    # Pressure correction term (Eq. 9)
    pres_term = (1 - spec_P[:, np.newaxis] / 1000 * pres_coef)  # Shape: (spec_SDN, 1)
    
    # Apply pressure correction to ESW_in_situ (element-wise multiplication)
    ESW_in_situ_p = ESW_in_situ * pres_term  # Shape: (spec_SDN, n_wavelength)

    # ************************************************************************
    # Calculate absorbance
    # ************************************************************************    
    
    # Compute the total absorbance (ABS_SW) from the UV intensity and dark-corrected reference spectrum
    # Note that the reference spectrum is already dark corrected
    ABS_SW = -np.log10(spec_UV_INTEN / E_ref)  

    # Compute the in situ bromide absorbances based on salinity and ESW_in_situ_p
    ABS_Br_tcor = ESW_in_situ_p * spec_S[:, np.newaxis] 
        
    # Subtract bromide absorbance from the total absorbance to get nitrate + baseline absorbance
    ABS_cor = ABS_SW - ABS_Br_tcor 

    # ************************************************************************
    # Calculate the nitrate concentration, baseline slope, and intercept of the baseline absorbance.
    # baseline absorbance. Following the example here: 
    # https://github.com/SOCCOM-BGCArgo/ARGO_PROCESSING/blob/master/MFILES/FLOATS/calc_FLOAT_NO3.m
    # ************************************************************************

    # Prepare fit matrix (M) and pseudo-inverse (M_INV)
    Ones = np.ones_like(E_N)
    M = np.column_stack([E_N, Ones / 100, WL / 1000])  # Wavelength x 3
    M_INV = np.linalg.pinv(M)

    # Perform the nitrate concentration calculation
    NO3 = calculate_no3_concentration(ABS_cor, E_N, WL, M, M_INV)

    # Return the result as a DataFrame
    no3_concentration = pd.DataFrame(data=NO3, index=spec_SDN, 
                                     columns=['Nitrate concentration (μM)', 'Baseline Intercept', 
                                              'Baseline Slope', 'RMS Error', 'Wavelength @ 240nm', 
                                              'Absorbance @ 240nm'])
    
    return no3_concentration, WL, E_N, E_S, ESW_in_situ, ESW_in_situ_p, ABS_SW, ABS_Br_tcor, ABS_cor, spec_UV_INTEN



# Calculate nitrate concentration, baseline slope, and intercept
def calculate_no3_concentration(ABS_cor, E_N, WL, M, M_INV):
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
        ABS_BL = WL * NO3[i, 2] + NO3[i, 1]
        ABS_NO3 = ABS_cor[i, :] - ABS_BL
        ABS_NO3_EXP = E_N * NO3[i, 0]
        FIT_DIF = ABS_NO3 - ABS_NO3_EXP

        # Calculate RMS error, but only if there are valid points
        if np.sum(tg) > 0:
            RMS_ERROR = np.sqrt(np.sum(FIT_DIF[tg] ** 2) / np.sum(tg))
        else:
            RMS_ERROR = np.nan  # Assign NaN if no valid points

        # Store RMS error and absorbance near 240 nm
        ind_240 = np.argmin(np.abs(WL - 240))
        ABS_240 = [WL[ind_240], ABS_cor[i, ind_240]]
        NO3[i, 3:] = [RMS_ERROR, *ABS_240]

    return NO3


def plot_corrected_data(WL_UV, E_S_interp, E_N_interp, ESW_in_situ, ESW_in_situ_p,
                        ABS_SW, ABS_Br_tcor, ABS_cor, time, timestamps, mooring_config, 
                        instrument, savepath=None):
    """
    Plot mooring data with four subplots to show results after corrections:
    A. Extinction coefficients
    B. Total absorbancc
    C. Bromide absorbance 
    D. Nitrate and baseline absorbance

    Parameters:
    -----------
    WL_UV : array-like
        Wavelength UV data.
    E_S_interp, E_N_interp, ESW_in_situ, ESW_in_situ_p : array-like
        Calibration data and correction factors.
    ABS_SW, ABS_Br_tcor, ABS_cor : array-like
        Absorbance data for different conditions.
    time : pandas.Index or array-like
        Timestamps for labeling.
    timestamps : list of int
        Indices for plotting in subplots B, C, and D.
    mooring_config : dict
        Mooring information
    instrument : str
        ID for mooring used in plot titles.
    savepath : str or Path, optional
        File path to save the figure. If None (default), the plot is displayed but not saved.
    """
    
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    titles = ['Total absorbance', 'Bromide absorbance', 'Absorbance (Nitrate and baseline)']
    data = [ABS_SW, ABS_Br_tcor, ABS_cor]
    labels = ['A', 'B', 'C', 'D']
    
    # Subplot A
    ax = axes[0, 0]
    ax.plot(WL_UV, E_S_interp, label='$\epsilon$ for bromide (uncorrected)')
    ax.plot(WL_UV, E_N_interp, label='$\epsilon$ for NO3')
    ax.plot(WL_UV, ESW_in_situ[timestamps[0], :], 'C3', lw=3, label='$\epsilon$ for bromide (temp corrected)')
    ax.plot(WL_UV, ESW_in_situ_p[timestamps[0], :], 'k--', lw=1, label='$\epsilon$ for bromide (temp + pressure corrected)')
    ax.legend()
    ax.set(ylabel='$\epsilon$', title=f'{mooring_config["MooringID"]}, {instrument}, {time[timestamps[0]]}')
    ax.annotate(labels[0], xy=(-0.15, 1.05), xycoords='axes fraction', fontsize=14, fontweight='bold')

    # Subplots B, C, and D
    for i, ax in enumerate(axes.flat[1:], start=1):
        for idx in timestamps:
            ax.plot(WL_UV, data[i - 1][idx, :], label=f'{time[idx]}')
        ax.legend()
        ax.set(ylabel=titles[i - 1], title=f'{mooring_config["MooringID"]}, {instrument}')
        ax.annotate(labels[i], xy=(-0.15, 1.05), xycoords='axes fraction', fontsize=14, fontweight='bold')
    
    fig.tight_layout()
    if savepath:
        fig.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.show()


def plot_intensity(ncal, nitrate_data_filtered, timestamps, mooring_config, instrument, 
                   inst_shortname='suna', savepath=None):
    """
    Plot dark-corrected intensity for selected timestamps with a DIW reference and highlight region.

    Parameters:
    -----------
    ncal : dict
        Dictionary containing 'WL' for wavelength data and 'Ref' for DIW reference values.
    nitrate_data_filtered : DataFrame
        Filtered data containing intensity values and dark correction values.
    timestamps : list of int
        Indices to use for plotting selected timestamps.
    mooring_id : str
        Mooring ID for plot title.
    instrument : str
        Instrument ID for plot title.
    inst_shortname : str, optional
        Short name for the instrument type ('suna' or 'isus').
        Determines which dark value column and UV spectral range to use.
        Defaults to 'suna'.
    savepath : str or Path, optional
        File path to save the figure. If None (default), the plot is displayed but not saved.
    """
    
    # === Instrument-specific dark value and slice ===
    if inst_shortname.lower() == 'suna':
        dark_col = 'Dark value used for fit'
        uv_slice = slice(9, 265)   # adjust if needed for your SUNA file
    elif inst_shortname.lower() == 'isus':
        dark_col = 'Sea-Water Dark Calculation'
        uv_slice = slice(17, 273)  # adjust if needed for your ISUS file
    else:
        raise ValueError("inst_shortname must be 'suna' or 'isus'.")

    fig, ax = plt.subplots(1, 1, figsize=(7, 4))
    
    for idx in timestamps:
        intensity = nitrate_data_filtered.iloc[idx, uv_slice] - nitrate_data_filtered[dark_col].iloc[idx]
        ax.plot(ncal['WL'], intensity, label=f'{nitrate_data_filtered.index[idx]}')

    ax.plot(ncal['WL'], ncal['Ref'], 'k--', label='DIW Reference')
    ax.axvspan(217, 240, color='gray', alpha=0.1)
    ax.set(
        xlim=[210, 300],
        ylim=[0, 67000],
        ylabel='Intensity (dark-corrected)',
        xlabel='Wavelength (nm)',
        title=f'{mooring_config["MooringID"]}, {instrument}, Dark-corrected intensity compared with reference'
    )
    ax.legend()
    
    if savepath:
        fig.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.show()


def plot_nitrate_and_rmse(nitrate_data_filtered, no3_concentration, ylim=(0, 30), 
                          inst_shortname='suna', savepath=None):
    """
    Generate two subplots comparing original and TS-corrected nitrate concentration and RMSE.

    Parameters:
    -----------
    nitrate_data_filtered : DataFrame
        DataFrame containing original nitrate concentration and RMSE values.
    no3_concentration : DataFrame
        DataFrame containing corrected nitrate concentration and RMS error values.
    ylim : tuple, optional
        Limits for the y-axis in the nitrate concentration plot. Default is (0, 30).
    inst_shortname : str, optional
        Short name for instrument type ('suna' or 'isus'). Used to pick correct column names.
    savepath : str or Path, optional
        File path to save the figure. If None (default), the plot is displayed but not saved.
    """
    
    # === Dynamic column names ===
    if inst_shortname.lower() == 'suna':
        nitrate_col = 'Nitrate concentration, μM'
        rmse_col = 'Fit RMSE'
    elif inst_shortname.lower() == 'isus':
        nitrate_col = 'NO3_conc'
        rmse_col = 'RMS Error'
    else:
        raise ValueError("inst_shortname must be 'suna' or 'isus'.")

    fig, axes = plt.subplots(2, 1, figsize=(8, 7))

    # Nitrate concentration plot
    ax = axes[0]
    nitrate_data_filtered[nitrate_col].plot(ax=ax, label='Original (after simple screening)')
    no3_concentration['Nitrate concentration (μM)'].plot(ax=ax, label='TS-corrected', color='C1')
    ax.legend()
    ax.set(title='Nitrate concentration (μM)', ylim=ylim)

    # RMSE plot
    ax = axes[1]
    nitrate_data_filtered[rmse_col].plot(ax=ax, label='Original (after simple screening)')
    no3_concentration['RMS Error'].plot(ax=ax, label='TS-corrected', color='C1')
    ax.legend()
    ax.set(title='RMSE')

    fig.tight_layout()
    if savepath:
        fig.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.show()


def qc_nitrate(no3_concentration, nitrate_data_filtered, rmse_cutoff=0.0035, 
               window_size=50, error_bar=0.0002, ylim=(0, 29), inst_shortname='suna', savepath=None):
    """
    Filter and analyze nitrate concentration data based on user-defined RMSE cutoff, 
    smoothing parameters, and error band, then plot the results in three subplots.
    
    Parameters:
    -----------
    no3_concentration : DataFrame
        DataFrame containing nitrate concentration and RMSE values.
    nitrate_data_filtered : DataFrame
        DataFrame containing the original nitrate concentration data.
    rmse_cutoff : float, optional
        Maximum allowed RMSE value for filtering (default is 0.0035).
    window_size : int, optional
        Window size for rolling mean (default is 50).
    error_bar : float, optional
        Error tolerance around the smoothed curve for further filtering (default is 0.0002).
    ylim : tuple, optional
        Y-axis limits for the nitrate concentration plot (default is (5, 29)).
    inst_shortname : str, optional
        Short name for instrument type ('suna' or 'isus'). Used to pick correct column names.
    savepath : str or Path, optional
        File path to save the figure. If None (default), the plot is displayed but not saved.
    """

    # === Dynamic column names ===
    if inst_shortname.lower() == 'suna':
        nitrate_col = 'Nitrate concentration, μM'
    elif inst_shortname.lower() == 'isus':
        nitrate_col = 'NO3_conc'
    else:
        raise ValueError("inst_shortname must be 'suna' or 'isus'.")
    
    # QC1: Filter data based on RMSE cutoff
    no3_concentration_QC1 = no3_concentration[
        ((no3_concentration['RMS Error'] > 0) & 
         (no3_concentration['RMS Error'] <= rmse_cutoff)) | 
        (no3_concentration['RMS Error'].isna())
    ]

    # === Rolling smoothing ===
    rmse_smoothed = no3_concentration_QC1['RMS Error'].rolling(
        window=window_size, center=True, 
        min_periods=(int(window_size * 0.6))  # Require >60% non-NaN values
    ).mean()
    
    # QC2: Filter values within the band range
    upper_bound = rmse_smoothed + error_bar
    lower_bound = rmse_smoothed - error_bar
    
    no3_concentration_QC2 = no3_concentration_QC1[
        ((no3_concentration_QC1['RMS Error'] >= lower_bound) &
         (no3_concentration_QC1['RMS Error'] <= upper_bound)) |
        (no3_concentration_QC1['RMS Error'].isna())
    ]
    
    # === Plotting ===
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 10), sharex=True)

    ax1.plot(no3_concentration_QC1.index, no3_concentration_QC1['RMS Error'], 
             label='TS_corrected+QC1', color='C1', alpha=0.6)
    ax1.plot(rmse_smoothed.index, rmse_smoothed, 
             label='Smoothed', color='blue', linewidth=2)
    ax1.fill_between(rmse_smoothed.index, lower_bound, upper_bound, 
                     color='blue', alpha=0.2, label=f'+/- {error_bar} Band')
    ax1.set_ylabel('RMS Error')
    ax1.legend(loc='upper right')
    ax1.set_title('RMS Error Analysis (Smoothed and QC1)')

    ax2.plot(no3_concentration_QC1.index, no3_concentration_QC1['RMS Error'], 
             label='TS_correct+QC1', color='C1', alpha=0.5)
    ax2.plot(no3_concentration_QC2.index, no3_concentration_QC2['RMS Error'], 
             label='TS_correct+QC1+QC2', color='green', linestyle='None', marker='o', markersize=1)
    ax2.set_ylabel('RMS Error')
    ax2.legend(loc='upper right')
    ax2.set_title('RMS Error Analysis (QC1 and QC2)')

    ax3.plot(nitrate_data_filtered.index, nitrate_data_filtered[nitrate_col], 
             label='Original (after simple screening)')
    ax3.plot(no3_concentration.index, no3_concentration['Nitrate concentration (μM)'], 
             label='TS_corrected', color='C1', lw=2.0)
    ax3.plot(no3_concentration_QC2.index, no3_concentration_QC2['Nitrate concentration (μM)'], 
             label='TS_correct+QC1+QC2', color='C2', lw=1.0)
    ax3.set_ylabel('Nitrate concentration (μM)')
    ax3.set_ylim(ylim)
    ax3.legend(loc='upper right')
    ax3.set_title('Nitrate Concentration (Original, TS-corrected, and QC-ed)')
    ax3.set_xlabel('Time')

    fig.tight_layout()
    if savepath:
        fig.savefig(savepath, dpi=150, bbox_inches='tight')
    plt.show()

    return no3_concentration_QC2

def calculate_mean_offset(curve_data, reference_points, max_timedelta=None):
    """
    Calculate the mean offset between a data curve and reference points.
    For each reference point, the closest non-NaN value in the curve is used.

    Parameters:
    -----------
    curve_data : pd.Series
        Time series data representing the curve to adjust.
    reference_points : list of tuples
        List of (index, value) tuples where `index` is a datetime and `value` is the reference value.
    max_timedelta : pd.Timedelta or None
        Optional. If provided, only matches within this time window are considered.

    Returns:
    --------
    float
        The mean offset between the curve and the reference points.
    """
    offsets = []
    curve_times = curve_data.index
    valid_curve = curve_data.dropna()

    for ref_index, ref_value in reference_points:
        try:
            # Make sure ref_index is datetime
            ref_index = pd.to_datetime(ref_index)

            # Compute time differences
            time_deltas = np.abs(valid_curve.index - ref_index)

            if max_timedelta is not None:
                within_window = time_deltas <= max_timedelta
                if not within_window.any():
                    print(f"No non-NaN values within {max_timedelta} of {ref_index}")
                    continue
                closest_idx = np.argmin(time_deltas[within_window])
                closest_time = valid_curve.index[within_window][closest_idx]
            else:
                closest_idx = np.argmin(time_deltas)
                closest_time = valid_curve.index[closest_idx]

            curve_value_at_closest = valid_curve.loc[closest_time]
            offset = curve_value_at_closest - ref_value

            offsets.append(offset)

            print(f"Ref time: {ref_index} | Closest non-NaN: {closest_time} | "
                  f"Curve value: {curve_value_at_closest:.3f} | Ref value: {ref_value} | Offset: {offset:.3f}")

        except Exception as e:
            print(f"Failed for {ref_index}: {e}")

    mean_offset = np.mean(offsets) if offsets else np.nan
    return mean_offset