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


# ============================================================================
# Public API - Simplified wrapper functions for common use cases
# ============================================================================

def range_check(
    data: pd.Series,
    min_val: float,
    max_val: float,
    flag_good: int = 1,
    flag_bad: int = 4,
) -> np.ndarray:
    """
    Simplified wrapper for gross range testing.

    Args:
        data (pd.Series): The data series to check.
        min_val (float): Minimum acceptable value.
        max_val (float): Maximum acceptable value.
        flag_good (int): Flag value for good data (default: 1).
        flag_bad (int): Flag value for bad data (default: 4).

    Returns:
        np.ndarray: Array of QC flags.
    """
    # Convert to Series if needed
    if isinstance(data, np.ndarray):
        data = pd.Series(data)
    
    config = {'min': min_val, 'max': max_val}
    flags = gross_range_test(data, config)
    
    # Apply custom flag values if specified
    if flag_good != 1 or flag_bad != 4:
        flags = flags.replace({1: flag_good, 4: flag_bad})
    
    return flags.values


def spike_detection(
    data: np.ndarray,
    threshold: float = 3.0,
    window: int = 5,
    method: str = "median",
) -> np.ndarray:
    """
    Simplified wrapper for spike detection.

    Args:
        data (np.ndarray): The data array to check.
        threshold (float): Threshold for spike detection (default: 3.0).
        window (int): Window size for median filter (default: 5).
        method (str): Detection method - "median" (default) or "stddev".

    Returns:
        np.ndarray: Array of QC flags.

    Raises:
        ValueError: If method is not "median" or "stddev".
    """
    if method not in ["median", "stddev"]:
        raise ValueError(f"Invalid method: {method}. Use 'median' or 'stddev'.")
    
    # Convert to Series if needed
    if isinstance(data, np.ndarray):
        data = pd.Series(data)
    
    config = {'window': window, 'threshold': threshold}
    flags = spike_test(data, config)
    
    return flags.values


def rate_of_change_check(
    data: np.ndarray,
    max_rate: float,
    flag_good: int = 1,
    flag_questionable: int = 3,
) -> np.ndarray:
    """
    Simplified wrapper for rate of change checking.

    Args:
        data (np.ndarray): The data array to check.
        max_rate (float): Maximum acceptable rate of change.
        flag_good (int): Flag for acceptable change (default: 1).
        flag_questionable (int): Flag for excessive change (default: 3).

    Returns:
        np.ndarray: Array of QC flags.
    """
    if isinstance(data, np.ndarray):
        data = pd.Series(data)
    
    config = {'threshold': max_rate}
    flags = gradient_test(data, config)
    
    # Use flag_questionable instead of 4 for rate of change
    flags = flags.replace({4: flag_questionable, 1: flag_good})
    
    return flags.values


def apply_all_checks(
    data: pd.DataFrame,
    ranges: dict = None,
    spike_threshold: float = 3.0,
    max_rate: dict = None,
    window: int = 5,
) -> pd.DataFrame:
    """
    Apply all QC checks to a DataFrame.

    Args:
        data (pd.DataFrame): Input data with columns like 'temperature', 'salinity'.
        ranges (dict): Dictionary with min/max ranges for each parameter.
                      e.g., {'temperature': (-2, 30), 'salinity': (0, 40)}
        spike_threshold (float): Threshold for spike detection (default: 3.0).
        max_rate (dict): Dictionary with max rate values for each parameter.
                        e.g., {'temperature': 0.5, 'salinity': 0.1}
        window (int): Window size for spike detection (default: 5).

    Returns:
        pd.DataFrame: DataFrame with added QC flag columns.
    """
    result = data.copy()
    
    # Apply range checks
    if ranges:
        for param, (min_val, max_val) in ranges.items():
            if param in result.columns:
                result[f'{param}_QC'] = range_check(result[param].values, min_val, max_val)
    
    # Apply spike detection to each column
    if 'spike_QC' not in result.columns and len(result.columns) > 0:
        # Apply to first data column if no specific column given
        first_col = result.columns[0]
        if first_col in result.columns:
            result['spike_QC'] = spike_detection(result[first_col].values, threshold=spike_threshold, window=window)
    
    # Apply rate of change checks
    if max_rate:
        for param, rate in max_rate.items():
            if param in result.columns:
                result[f'{param}_rate_QC'] = rate_of_change_check(result[param].values, rate)
    
    return result
