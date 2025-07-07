import numpy as np
import pytest
from geotools import latlon_convert, rotate_coord

# Test for latlon_convert
def test_latlon_convert_north_west():
    """Test standard conversion for North latitude and West longitude."""
    lat_str = "45 30.00 N"
    lon_str = "120 15.00 W"
    expected_lat = 45 + 30/60.
    expected_lon = 120 + 15/60.
    lat, lon = latlon_convert(lat_str, lon_str)
    assert np.isclose(lat, expected_lat)
    assert np.isclose(lon, expected_lon)

def test_latlon_convert_north_east():
    """Test conversion for North latitude and East longitude (should be negative lon)."""
    lat_str = "30 00.00 N"
    lon_str = "075 45.00 E"
    expected_lat = 30.0
    expected_lon = -(75 + 45/60.) # East is negative
    lat, lon = latlon_convert(lat_str, lon_str)
    assert np.isclose(lat, expected_lat)
    assert np.isclose(lon, expected_lon)

def test_latlon_convert_south_west():
    """Test conversion for South latitude (should be negative lat) and West longitude."""
    lat_str = "10 10.00 S"
    lon_str = "060 20.00 W"
    expected_lat = -(10 + 10/60.) # South is negative
    expected_lon = 60 + 20/60.
    lat, lon = latlon_convert(lat_str, lon_str)
    assert np.isclose(lat, expected_lat)
    assert np.isclose(lon, expected_lon)

def test_latlon_convert_south_east():
    """Test conversion for South latitude (negative lat) and East longitude (negative lon)."""
    lat_str = "05 05.00 S"
    lon_str = "170 30.00 E"
    expected_lat = -(5 + 5/60.)
    expected_lon = -(170 + 30/60.)
    lat, lon = latlon_convert(lat_str, lon_str)
    assert np.isclose(lat, expected_lat)
    assert np.isclose(lon, expected_lon)

def test_latlon_convert_zero_minutes():
    """Test conversion with zero minutes part."""
    lat_str = "90 00.00 N"
    lon_str = "000 00.00 W"
    expected_lat = 90.0
    expected_lon = 0.0
    lat, lon = latlon_convert(lat_str, lon_str)
    assert np.isclose(lat, expected_lat)
    assert np.isclose(lon, expected_lon)

def test_latlon_convert_with_spaces():
    """Test conversion with extra spaces in input strings."""
    lat_str = " 45   30.00   N "
    lon_str = " 120   15.00   W "
    expected_lat = 45 + 30/60.
    expected_lon = 120 + 15/60.
    lat, lon = latlon_convert(lat_str, lon_str)
    assert np.isclose(lat, expected_lat)
    assert np.isclose(lon, expected_lon)

# Test for rotate_coord
def test_rotate_coord_no_declination():
    """Test rotation with zero declination correction."""
    u = np.array([1.0, 0.0, -1.0, 0.0]) # East, North, West, South
    v = np.array([0.0, 1.0, 0.0, -1.0])
    
    uu, vv = rotate_coord(u, v, declination_corr=0.0)
    
    assert np.allclose(uu, u)
    assert np.allclose(vv, v)

def test_rotate_coord_positive_declination():
    """Test rotation with a positive (eastward) declination."""
    u = np.array([0.0]) # Pure North
    v = np.array([1.0])
    declination = 90.0 # Rotate 90 degrees East (North becomes East)
    
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    
    assert np.isclose(uu[0], 1.0) # New u should be 1 (East)
    assert np.isclose(vv[0], 0.0) # New v should be 0

    u = np.array([1.0]) # Pure East
    v = np.array([0.0])
    declination = 90.0 # Rotate 90 degrees East (East becomes South)
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    assert np.isclose(uu[0], 0.0)
    assert np.isclose(vv[0], -1.0) # South

def test_rotate_coord_negative_declination():
    """Test rotation with a negative (westward) declination."""
    u = np.array([0.0]) # Pure North
    v = np.array([1.0])
    declination = -90.0 # Rotate 90 degrees West (North becomes West)
    
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    
    assert np.isclose(uu[0], -1.0) # New u should be -1 (West)
    assert np.isclose(vv[0], 0.0) # New v should be 0

    u = np.array([1.0]) # Pure East
    v = np.array([0.0])
    declination = -90.0 # Rotate 90 degrees West (East becomes North)
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    assert np.isclose(uu[0], 0.0)
    assert np.isclose(vv[0], 1.0) # North

def test_rotate_coord_mixed_values():
    """Test rotation with a mix of values and special 'bad' values (1e35)."""
    u = np.array([1.0, 1e35, 0.5])
    v = np.array([0.0, 2.0, 1e35])
    declination = 45.0
    
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    
    # Expected values for (1.0, 0.0) rotated by 45 degrees:
    # mag = 1, direc = 0 (East). New direc = 0 + pi/4.
    # uu = 1 * sin(pi/4) = 1/sqrt(2) approx 0.707
    # vv = 1 * cos(pi/4) = 1/sqrt(2) approx 0.707
    assert np.isclose(uu[0], 1.0 / np.sqrt(2))
    assert np.isclose(vv[0], 1.0 / np.sqrt(2))

    # Second element: u is 1e35, v is 2.0. u should remain 1e35.
    # v is not 1e35, so it should be rotated based on current (1e35, 2.0) direction.
    # However, the logic for 1e35 is slightly flawed:
    # `v_ind = (v == 1e35)` is used to reset `vv[v_ind] = 1e35`.
    # This means if v is NOT 1e35, it will be rotated, even if u IS 1e35.
    # It seems the intention is to propagate 1e35 if *either* u or v is 1e35 for that point.
    # As per the current code, only the exact 1e35 values in the *output* are set.
    # Let's test based on the *current* implementation:
    assert np.isclose(uu[1], 1e35) # u was 1e35
    assert not np.isclose(vv[1], 1e35) # v was 2.0, so it gets rotated.
    # Mag = sqrt(1e35^2 + 2^2) ~ 1e35. direc = arctan2(1e35, 2) ~ pi/2.
    # new_direc = pi/2 + pi/4 = 3pi/4.
    # uu = 1e35 * sin(3pi/4) ~ 1e35 * 0.707
    # vv = 1e35 * cos(3pi/4) ~ 1e35 * -0.707
    # This is a very large number, so let's just confirm it's not 1e35, and not finite in a specific way.
    # A more robust test would consider the implications of 1e35 for rotation.
    
    # Third element: u is 0.5, v is 1e35. v should remain 1e35.
    assert not np.isclose(uu[2], 1e35) # u was 0.5, so it gets rotated.
    assert np.isclose(vv[2], 1e35) # v was 1e35

    # If the intent for 1e35 is to be a "missing value" flag that propagates, the `rotate_coord` logic would need to be adjusted.
    # For now, these tests confirm the *current* behavior of the provided code.

def test_rotate_coord_all_special_values():
    """Test case where both u and v are 1e35."""
    u = np.array([1e35])
    v = np.array([1e35])
    declination = 10.0
    
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    
    assert np.isclose(uu[0], 1e35)
    assert np.isclose(vv[0], 1e35)

def test_rotate_coord_all_nan_values():
    """Test case where both u and v are missing/nan."""
    u = np.array([np.nan])
    v = np.array([np.nan])
    declination = 10.0
    
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    
    assert np.isclose(uu[0], np.nan)
    assert np.isclose(vv[0], np.nan)

def test_rotate_coord_single_value():
    """Test with single float inputs (not arrays)."""
    u = 1.0
    v = 1.0
    declination = 45.0
    
    uu, vv = rotate_coord(u, v, declination_corr=declination)
    
    # (1,1) rotated by 45 degrees:
    # mag = sqrt(2), direc = pi/4. New direc = pi/4 + pi/4 = pi/2.
    # uu = sqrt(2) * sin(pi/2) = sqrt(2) approx 1.414
    # vv = sqrt(2) * cos(pi/2) = 0
    assert np.isclose(uu, np.sqrt(2))
    assert np.isclose(vv, 0.0)