import numpy as np
import pandas as pd
import xarray as xr


def outlier_bounds_std(arr, multiplier=3):
    r"""
    Mask values outside the upper and lower outlier limits by standard
    deviation

        :math:`\mu \pm 3\sigma`

    the multiplier [3] can be adjusted by the user
    returns the lower_limit, upper_limit

    Parameters
    ----------
    arr : np.array|xr.DataArray, dtype=float, shape=[n, ]
        the full timeseries of the entire dataset
    multiplier : float=1.5
        sets the standard deviation multiplier

    Returns
    -------
    xr.Dataset
        A new xarray Dataset with the filtered variable and a corresponding
        quality control (QC) variable.
        QC flags:
        0: Good data
        1: Data at beginning/end of series (not processed by rolling filter)
        4: Data flagged as outlier and replaced with NaN (before interpolation)
        8: Data that was originally an outlier (flag 4) and subsequently interpolated
    """

    arr = np.array(arr)
    mean = np.nanmean(arr)
    std = np.nanstd(arr)
    ll = mean - std * multiplier
    ul = mean + std * multiplier
    mask = (arr < ll) | (arr > ul)
    arr[mask] = np.nan
    return arr


def outlier_bounds_iqr(arr, multiplier=1.5):
    r"""
    Mask values outside the upper/lower outlier limits by interquartile range:

    .. math::

        lim_{low} = Q_1 - 1.5\cdot(Q_3 - Q_1)\\
        lim_{up} = Q_3 + 1.5\cdot(Q_3 - Q_1)

    the multiplier [1.5] can be adjusted by the user
    returns the lower_limit, upper_limit

    Parameters
    ----------
    arr : np.array|xr.DataArray, dtype=float, shape=[n, ]
        the full timeseries of the entire dataset
    multiplier : float=1.5
        sets the interquartile range

    Returns
    -------
    arr : array | xarray.DataArray
        A data object where values outside the limits are masked.
        Metdata will be preserved if the original input array is xr.DataArray


    """

    arr = np.array(arr)
    q1, q3 = np.nanpercentile(arr, [25, 75])
    iqr = q3 - q1
    ll = q1 - iqr * multiplier
    ul = q3 + iqr * multiplier
    mask = (arr < ll) | (arr > ul)
    arr[mask] = np.nan
    return arr

def rolling_outlier_std(tdf, var_choice=None, timebase=1, stddev=1, interp_fill_timebase='1h'):
    """[summary]

    Args:
        xdf ([xarray]):  xarray dataset.
        var_choice (string, optional):  string name of variable to filter
        timebase (int, optional): [time window value to be applied to rolling]. Defaults to 1.
        stddev (int, optionl): [standard deviation threshold to use to filter data out]. Defaults to 1.
    """

    xdf = tdf.copy()
    r = (xdf[var_choice] - xdf.rolling(time=timebase, center=True).median()[var_choice])
    rc = outlier_bounds_std(r, stddev)

    xdf[var_choice] = (xdf[var_choice].where(~np.isnan(rc))).interpolate_na(dim='time', max_gap=interp_fill_timebase)

    # QC flag: 4 for outlier, 0 for good, 8 for interpolated, 1 for edge
    xdf[var_choice + '_QC'] = xr.zeros_like(xdf[var_choice])
    xdf[var_choice + '_QC'] = xdf[var_choice].where((~np.isnan(rc)), 4)
    xdf[var_choice + '_QC'].values[xdf[var_choice + '_QC'].values != 4] = 0

    mask = (tdf[var_choice].where(~np.isnan(rc)))
    mask_QC = xdf[var_choice].where(((xdf[var_choice] == mask) | np.isnan(xdf[var_choice])), 8)
    xdf[var_choice + '_QC'].values[(mask_QC.values) == 8] = 8

    xdf[var_choice][:round(timebase/2)+1] = tdf[var_choice][:round(timebase/2)+1]
    xdf[var_choice+'_QC'][:round(timebase/2)+1] = tdf[var_choice][:round(timebase/2)+1]*0 +1
    xdf[var_choice][-1*round(timebase/2)-1:] = tdf[var_choice][-1*round(timebase/2)-1:] 
    xdf[var_choice+'_QC'][-1*round(timebase/2)-1:] = tdf[var_choice][-1*round(timebase/2)-1:]*0 +1 

    return xdf


def rolling_outlier_pd(
    df: pd.DataFrame, column: str = 'salinity', window_size: str = '7D', num_std_dev: int = 5
) -> pd.DataFrame:
    """
    Apply a rolling standard deviation filter to a column of a pandas DataFrame.
    Outliers are set to NaN.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing the column to filter.
    column : str, default='salinity'
        Name of the column to filter.
    window_size : str, default='7D'
        Size of the rolling window (e.g., '7D' for 7 days).
    num_std_dev : int, default=5
        Number of standard deviations for outlier threshold.

    Returns
    -------
    pd.DataFrame
        DataFrame with outliers replaced by NaN in the specified column.
    """
    df_filtered = df.copy()
    mean_col = f'{column}_rolling_mean'
    std_col = f'{column}_rolling_std'
    upper_col = f'{column}_upper_bound'
    lower_col = f'{column}_lower_bound'

    df_filtered[mean_col] = df_filtered[column].rolling(window=window_size).mean()
    df_filtered[std_col] = df_filtered[column].rolling(window=window_size).std()
    df_filtered[upper_col] = df_filtered[mean_col] + num_std_dev * df_filtered[std_col]
    df_filtered[lower_col] = df_filtered[mean_col] - num_std_dev * df_filtered[std_col]

    outlier_mask = (df_filtered[column] > df_filtered[upper_col]) | (df_filtered[column] < df_filtered[lower_col])
    df_filtered.loc[outlier_mask, column] = np.nan

    df_filtered = df_filtered.drop(columns=[mean_col, std_col, upper_col, lower_col])
    return df_filtered
