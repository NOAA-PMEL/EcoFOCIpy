import gsw
import numpy as np
import pandas as pd

def gross_range_test(data: pd.Series, config: dict) -> pd.Series:
    """
    Checks if the data is within the configured min/max range.

    Args:
        data (pd.Series): The data series to check (e.g., temperature).
        config (dict): A dictionary with 'min' and 'max' keys.

    Returns:
        pd.Series: A series of QC flags (1 for pass, 4 for fail).
    """
    flags = pd.Series(1, index=data.index)
    # Flag values outside the min/max range as bad (4)
    flags[ (data < config['min']) | (data > config['max']) ] = 4
    return flags

def spike_test(data: pd.Series, config: dict) -> pd.Series:
    """
    Detects spikes in the data using a running median.

    Args:
        data (pd.Series): The data series to check.
        config (dict): A dictionary with 'window' and 'threshold' keys.

    Returns:
        pd.Series: A series of QC flags (1 for pass, 4 for fail).
    """
    flags = pd.Series(1, index=data.index)
    window = config.get('window', 5) # Default window size of 5
    threshold = config['threshold']
    
    # Calculate the difference between the data and a centered rolling median
    median_diff = (data - data.rolling(window=window, center=True, min_periods=3).median()).abs()
    
    # Flag spikes as bad (4)
    flags[median_diff > threshold] = 4
    return flags

def stuck_value_test(data: pd.Series, config: dict) -> pd.Series:
    """
    Checks for stuck sensor values.

    Args:
        data (pd.Series): The data series to check.
        config (dict): A dictionary with a 'consecutive_limit' key.

    Returns:
        pd.Series: A series of QC flags (1 for pass, 4 for fail).
    """
    flags = pd.Series(1, index=data.index)
    limit = config['consecutive_limit']
    
    # Find where the difference between consecutive values is zero
    is_stuck = data.diff() == 0
    
    # A rolling sum over the boolean series can find consecutive stuck values
    stuck_count = is_stuck.rolling(window=limit).sum()
    
    # Flag points that are part of a 'stuck' sequence
    flags[stuck_count >= limit - 1] = 4
    return flags

def gradient_test(data: pd.Series, config: dict) -> pd.Series:
    """
    Checks for excessive gradients between consecutive points.

    Args:
        data (pd.Series): The data series to check.
        config (dict): A dictionary with a 'threshold' key.

    Returns:
        pd.Series: A series of QC flags (1 for pass, 4 for fail).
    """
    flags = pd.Series(1, index=data.index)
    threshold = config['threshold']
    
    # Calculate the absolute difference between consecutive points
    gradient = data.diff().abs()
    
    flags[gradient > threshold] = 4
    return flags

def density_inversion_test(df: pd.DataFrame, config: dict) -> pd.Series:
    """
    Checks for density inversions, indicating unstable water columns.
    This test requires pressure, practical salinity, and in-situ temperature.
    It returns flags for BOTH temperature and salinity.

    Args:
        df (pd.DataFrame): DataFrame containing 'pressure', 'salinity', 'temperature'.
        config (dict): A dictionary with a 'threshold' key for density difference.

    Returns:
        pd.Series: A series of QC flags (1 for pass, 4 for fail).
    """
    flags = pd.Series(1, index=df.index)
    threshold = config.get('threshold', -0.03) # Allow for small, non-impactful inversions

    # Ensure pressure is monotonically increasing for a clean diff
    df_sorted = df.sort_values('pressure').reset_index()

    # Calculate Absolute Salinity (SA) from Practical Salinity (SP)
    # Note: Using placeholder longitude and latitude. Replace if you have real values.
    lon = df_sorted.get('longitude', 0)
    lat = df_sorted.get('latitude', 0)
    sa = gsw.SA_from_SP(df_sorted['salinity'], df_sorted['pressure'], lon, lat)
    
    # Calculate Conservative Temperature (CT) from in-situ Temperature (t)
    ct = gsw.CT_from_t(sa, df_sorted['temperature'], df_sorted['pressure'])
    
    # Calculate seawater density (rho)
    rho = gsw.rho(sa, ct, df_sorted['pressure'])
    
    # Calculate the difference in density between levels
    density_diff = rho.diff()
    
    # Find inversions (density decreases with depth)
    # The original index is preserved in the 'index' column from reset_index()
    inversion_indices = df_sorted.loc[density_diff < threshold, 'index']
    
    flags.loc[inversion_indices] = 4
    return flags

def run_ctd_qc(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Main function to run all CTD QC tests.

    Args:
        df (pd.DataFrame): The input DataFrame with CTD data. 
                           Must contain 'pressure', 'temperature', 'salinity'.
        config (dict): A configuration dictionary for all QC tests.

    Returns:
        pd.DataFrame: The DataFrame with added QC flag columns.
    """
    # Create a copy to avoid modifying the original DataFrame
    df_qc = df.copy()

    # --- Initialize Flag Columns ---
    df_qc['temperature_qc'] = pd.Series(1, index=df_qc.index)
    df_qc['salinity_qc'] = pd.Series(1, index=df_qc.index)

    # --- Run Tests for Temperature ---
    tests_to_run = {
        'gross_range': gross_range_test,
        'spike': spike_test,
        'stuck_value': stuck_value_test,
        'gradient': gradient_test
    }
    
    for test_name, test_func in tests_to_run.items():
        if test_name in config['temperature']:
            flags = test_func(df_qc['temperature'], config['temperature'][test_name])
            # Combine flags: if a point fails any test, it's marked bad (4)
            df_qc['temperature_qc'] = np.maximum(df_qc['temperature_qc'], flags)

    # --- Run Tests for Salinity ---
    for test_name, test_func in tests_to_run.items():
        if test_name in config['salinity']:
            flags = test_func(df_qc['salinity'], config['salinity'][test_name])
            df_qc['salinity_qc'] = np.maximum(df_qc['salinity_qc'], flags)


    # --- Run Density Inversion Test ---
    # This test flags both temperature and salinity
    if 'density_inversion' in config:
        density_flags = density_inversion_test(df_qc, config['density_inversion'])
        df_qc['temperature_qc'] = np.maximum(df_qc['temperature_qc'], density_flags)
        df_qc['salinity_qc'] = np.maximum(df_qc['salinity_qc'], density_flags)


    return df_qc
