"""
Various mathematical transformations for convenience
"""
import numpy as np


def latlon_convert(Mooring_Lat, Mooring_Lon):
    """[summary]

    Args:
        Mooring_Lat (float): latitude as +DD MM.SS N
        Mooring_Lon (float): longitude as +DDD MM.SS W

    Returns:
        array(float, float): returns converted (Lat, Lon)
    """
    
    tlat = Mooring_Lat.strip().split() #deg min dir
    lat = float(tlat[0]) + float(tlat[1]) / 60.
    if tlat[2] == 'S':
        lat = -1 * lat
        
    tlon = Mooring_Lon.strip().split() #deg min dir
    lon = float(tlon[0]) + float(tlon[1]) / 60.
    if tlon[2] == 'E':
        lon = -1 * lon
        
    return (lat, lon)

def rotate_coord(u,v, declination_corr=0.0):
    """[summary]

    Args:
        u (float): u component +East
        v (float): v component +North
        declination_corr (float, optional): positive East. Defaults to 0.0

    Returns:
        float: rotated U, V
    """

    u_ind = (u == 1e35)
    v_ind = (v == 1e35)
    mag = np.sqrt(u**2 + v**2)
    direc = np.arctan2(u,v)
    direc =  direc + np.deg2rad(declination_corr)
    uu = mag * np.sin(direc)
    vv = mag * np.cos(direc)
    
    uu[u_ind] = 1e35
    vv[v_ind] = 1e35
    return (uu, vv)