import numpy as np
import pytest
from EcoFOCIpy.math.haversine import distance, nearest_point

# Constants for testing
EARTH_RADIUS_KM = 6371

# --- Tests for distance function ---

def test_distance_same_point():
    """Test distance between a point and itself should be zero."""
    origin = (0, 0)
    destination = (0, 0)
    assert distance(origin, destination) == 0.0


def test_distance_equator_half_world():
    """Test distance between two points on the equator 180 degrees apart."""
    origin = (0, 0)
    destination = (0, 180)
    # Half circumference of Earth
    expected_distance = np.pi * EARTH_RADIUS_KM
    assert np.isclose(distance(origin, destination), expected_distance, atol=0.1)


def test_distance_north_pole_south_pole():
    """Test distance between North Pole and South Pole."""
    origin = (90, 0)
    destination = (-90, 0)
    # Half circumference of Earth (through the poles)
    expected_distance = np.pi * EARTH_RADIUS_KM
    assert np.isclose(distance(origin, destination), expected_distance, atol=0.1)


def test_distance_known_points_small():
    """Test with two close points (e.g., within a city)."""
    # Seattle Space Needle to Pike Place Market
    # Lat/Lon from Google Maps
    origin = (47.6205, -122.3493)  # Space Needle
    destination = (47.6098, -122.3392)  # Pike Place Market
    # Expected distance from online calculator (~1.4 km) - https://www.omnicalculator.com/math/great-circle
    expected_distance = 1.41  # km
    assert np.isclose(distance(origin, destination), expected_distance, atol=0.05)


def test_distance_known_points_larger():
    """Test with two points across continents."""
    # New York City to London
    origin = (40.7128, -74.0060)  # NYC
    destination = (51.5074, 0.1278)  # London
    # Expected distance from online calculator (~5585 km) - https://www.omnicalculator.com/math/great-circle
    expected_distance = 5585.23  # km
    assert np.isclose(distance(origin, destination), expected_distance, atol=2.0)


def test_distance_symmetry():
    """Test that distance is symmetric."""
    point1 = (34.0522, -118.2437)  # Los Angeles
    point2 = (39.9042, 116.4074)  # Beijing
    dist1_to_2 = distance(point1, point2)
    dist2_to_1 = distance(point2, point1)
    assert np.isclose(dist1_to_2, dist2_to_1)

# --- Tests for nearest_point function ---

def test_nearest_point_1d_basic():
    """Test 1D grid with clear nearest point."""
    origin = (10, 10)
    latpoints = np.array([5, 10, 15])
    lonpoints = np.array([5, 10, 15])
    
    # The origin (10,10) is exactly on a grid point at (latpoints[1], lonpoints[1])
    dist_min, nearest_lat, nearest_lon, lat_idx, lon_idx = nearest_point(origin, latpoints, lonpoints, grid='1d')
    
    assert np.isclose(dist_min, 0.0)
    assert np.isclose(nearest_lat, 10.0)
    assert np.isclose(nearest_lon, 10.0)
    assert lat_idx == 1
    assert lon_idx == 1

def test_nearest_point_1d_offset():
    """Test 1D grid with nearest point not exactly on grid, and multiple options."""
    origin = (12, 12)
    latpoints = np.array([5, 10, 15, 20])
    lonpoints = np.array([5, 10, 15, 20])

    # Expected nearest is (10,10) or (10,15) or (15,10) or (15,15)
    # Let's verify it finds a point within the (10,10)-(15,15) square and has the minimum distance
    dist_min, nearest_lat, nearest_lon, lat_idx, lon_idx = nearest_point(origin, latpoints, lonpoints, grid='1d')
    
    # Calculate expected minimum distance manually
    d1 = distance(origin, (10, 10))
    d2 = distance(origin, (10, 15))
    d3 = distance(origin, (15, 10))
    d4 = distance(origin, (15, 15))
    expected_min_dist = min(d1, d2, d3, d4)

    assert np.isclose(dist_min, expected_min_dist)
    assert (nearest_lat == 10.0 or nearest_lat == 15.0)
    assert (nearest_lon == 10.0 or nearest_lon == 15.0)
    # The exact indices depend on the tie-breaking behavior of np.where, but they should point to one of the closest
    assert (lat_idx in [1, 2])
    assert (lon_idx in [1, 2])


def test_nearest_point_1d_single_point_grid():
    """Test 1D grid with only one point."""
    origin = (0, 0)
    latpoints = np.array([10])
    lonpoints = np.array([10])

    dist_min, nearest_lat, nearest_lon, lat_idx, lon_idx = nearest_point(origin, latpoints, lonpoints, grid='1d')

    expected_dist = distance(origin, (10, 10))
    assert np.isclose(dist_min, expected_dist)
    assert np.isclose(nearest_lat, 10.0)
    assert np.isclose(nearest_lon, 10.0)
    assert lat_idx == 0
    assert lon_idx == 0


def test_nearest_point_2d_basic():
    """Test 2D grid with clear nearest point."""
    origin = (10, 10)
    latpoints = np.array([[5, 5, 5], [10, 10, 10], [15, 15, 15]])
    lonpoints = np.array([[5, 10, 15], [5, 10, 15], [5, 10, 15]])

    dist_min, nearest_lat, nearest_lon, lat_idx, lon_idx = nearest_point(origin, latpoints, lonpoints, grid='2d')

    assert np.isclose(dist_min, 0.0)
    assert np.isclose(nearest_lat, 10.0)
    assert np.isclose(nearest_lon, 10.0)
    assert lat_idx == 1
    assert lon_idx == 1

def test_nearest_point_2d_offset():
    """Test 2D grid with nearest point not exactly on grid."""
    origin = (12, 12)
    latpoints = np.array([[5, 5, 5], [10, 10, 10], [15, 15, 15], [20, 20, 20]])
    lonpoints = np.array([[5, 10, 15], [5, 10, 15], [5, 10, 15], [5, 10, 15]])

    dist_min, nearest_lat, nearest_lon, lat_idx, lon_idx = nearest_point(origin, latpoints, lonpoints, grid='2d')
    
    # Expected nearest point is (10,10) or (10,15) or (15,10) or (15,15) from the grid.
    # The actual nearest point on the grid (10,10), (10,15), (15,10), (15,15)
    
    # Calculate distances to surrounding points in the grid
    distances_to_check = [
        distance(origin, (latpoints[1,1], lonpoints[1,1])), # (10,10)
        distance(origin, (latpoints[1,2], lonpoints[1,2])), # (10,15)
        distance(origin, (latpoints[2,1], lonpoints[2,1])), # (15,10)
        distance(origin, (latpoints[2,2], lonpoints[2,2]))  # (15,15)
    ]
    expected_min_dist = min(distances_to_check)

    assert np.isclose(dist_min, expected_min_dist, atol=1.0)
    assert (nearest_lat == 10.0 or nearest_lat == 15.0)
    assert (nearest_lon == 10.0 or nearest_lon == 15.0)
    assert (lat_idx in [1, 2])
    assert (lon_idx in [1, 2])


def test_nearest_point_2d_single_point_grid():
    """Test 2D grid with only one point."""
    origin = (0, 0)
    latpoints = np.array([[10]])
    lonpoints = np.array([[10]])
    
    dist_min, nearest_lat, nearest_lon, lat_idx, lon_idx = nearest_point(origin, latpoints, lonpoints, grid='2d')
    
    expected_dist = distance(origin, (10, 10))
    assert np.isclose(dist_min, expected_dist, atol=1.0)
    assert np.isclose(nearest_lat, 10.0)
    assert np.isclose(nearest_lon, 10.0)
    assert lat_idx == 0
    assert lon_idx == 0


def test_nearest_point_invalid_grid_type():
    """Test with an invalid grid type string."""
    origin = (0, 0)
    latpoints = np.array([1, 2])
    lonpoints = np.array([1, 2])

    # The current code would execute the '2d' block if 'grid' is not '1d'.
    # It might lead to an IndexError if latpoints/lonpoints are 1D arrays
    # but treated as 2D (e.g., latrow being a scalar).
    # A more robust implementation would raise a ValueError for unhandled grid types.

    # Given the current implementation, if `grid` is not '1d', it attempts '2d'.
    # If latpoints/lonpoints are 1D arrays, `latrow` will be a scalar in the inner loop,
    # leading to an `IndexError` when `latpoints[i,j]` is accessed, or a `TypeError` when `lonrow` is iterated.

    # Let's test for the expected error based on current behavior:
    with pytest.raises(Exception):
        nearest_point(origin, latpoints, lonpoints, grid='unknown_type')

    # If the intention was to handle this gracefully, a try-except or if-elif-else structure
    # that raises a specific ValueError would be better.
    # e.g., if grid not in ['1d', '2d']: raise ValueError("Invalid grid type")


def test_nearest_point_empty_latpoints_1d():
    """Test with empty latpoints array for 1D grid."""
    origin = (0, 0)
    latpoints = np.array([])
    lonpoints = np.array([1, 2])
    
    # np.zeros will create an array of shape (0, 2), which is fine.
    # The loops will not run, dist.min() will raise an error on empty array.
    with pytest.raises(ValueError, match="zero-size array to reduction operation minimum which has no identity"):
        nearest_point(origin, latpoints, lonpoints, grid='1d')

def test_nearest_point_empty_lonpoints_1d():
    """Test with empty lonpoints array for 1D grid."""
    origin = (0, 0)
    latpoints = np.array([1, 2])
    lonpoints = np.array([])
    
    with pytest.raises(ValueError, match="zero-size array to reduction operation minimum which has no identity"):
        nearest_point(origin, latpoints, lonpoints, grid='1d')

def test_nearest_point_empty_2d():
    """Test with empty 2D arrays."""
    origin = (0, 0)
    latpoints = np.array([[]])
    lonpoints = np.array([[]])
    
    # np.zeros_like will create an empty array.
    # The loops will try to iterate over empty rows/elements, `dist.min()` will fail.
    with pytest.raises(ValueError, match="zero-size array to reduction operation minimum which has no identity"):
        nearest_point(origin, latpoints, lonpoints, grid='2d')