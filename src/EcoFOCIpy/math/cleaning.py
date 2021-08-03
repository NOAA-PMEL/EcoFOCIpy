#modified from GliderTools.py

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
    arr : array | xarray.DataArray
        A data object where values outside the limits are masked.
        Metdata will be preserved if the original input array is xr.DataArray

    """

    from numpy import array, nan, nanmean, nanstd

    arr = array(arr)

    mean = nanmean(arr)
    std = nanstd(arr)

    ll = mean - std * multiplier
    ul = mean + std * multiplier

    mask = (arr < ll) | (arr > ul)
    arr[mask] = nan

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
    from numpy import array, nan, nanpercentile

    arr = array(arr)

    q1, q3 = nanpercentile(arr, [25, 75])
    iqr = q3 - q1

    ll = q1 - iqr * multiplier
    ul = q3 + iqr * multiplier

    mask = (arr < ll) | (arr > ul)
    arr[mask] = nan

    return arr

def rolling_outlier_std(tdf, var_choice=None, timebase=1, stddev=1, interp_fill_timebase=1):
    """[summary]

    Args:
        xdf ([xarray]):  xarray dataset.
        var_choice (string, optional):  string name of variable to filter
        timebase (int, optional): [time window value to be applied to rolling]. Defaults to 1.
        stddev (int, optionl): [standard deviation threshold to use to filter data out]. Defaults to 1.
    """
    from numpy import isnan
    from xarray import zeros_like

    xdf = tdf.copy()
    r = (xdf[var_choice] - xdf.rolling(time=timebase, center=True).median()[var_choice])
    rc = outlier_bounds_std(r,stddev)

    xdf[var_choice] = (xdf[var_choice].where(~isnan(rc))).interpolate_na(dim='time',max_gap=interp_fill_timebase)

    #mask values that are filtered out by algorithm
    xdf[var_choice+'_QC'] = zeros_like(xdf[var_choice])
    xdf[var_choice+'_QC'] = xdf[var_choice].where((~isnan(rc)),4)
    xdf[var_choice+'_QC'].values[xdf[var_choice+'_QC'].values !=4] = 0

    #mask values that are interpolated back in 
    mask = xdf[var_choice].where(xdf[var_choice] == (xdf[var_choice].where(~isnan(rc))).interpolate_na(dim='time',max_gap=interp_fill_timebase),8)
    mask.values[mask.values !=8] = 0
    xdf[var_choice+'_QC'].values[mask.values ==8] = 8

    xdf[var_choice][:round(timebase/2)+1] = tdf[var_choice][:round(timebase/2)+1]
    xdf[var_choice+'_QC'][:round(timebase/2)+1] = tdf[var_choice][:round(timebase/2)+1]*0 +1
    xdf[var_choice][-1*round(timebase/2)-1:] = tdf[var_choice][-1*round(timebase/2)-1:] 
    xdf[var_choice+'_QC'][-1*round(timebase/2)-1:] = tdf[var_choice][-1*round(timebase/2)-1:]*0 +1 

    return xdf