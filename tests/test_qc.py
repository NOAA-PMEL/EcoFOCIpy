"""
Unit tests for EcoFOCIpy Quality Control (QC) module.

Tests for QC flagging, data validation, and anomaly detection functions.
"""

import unittest
from typing import Tuple

import numpy as np
import pandas as pd

from EcoFOCIpy.qc import ctd_qc


class TestRangeCheck(unittest.TestCase):
    """Tests for range_check function."""

    def setUp(self):
        """Set up test data."""
        self.good_data = np.array([5.0, 10.0, 15.0, 20.0, 25.0])
        self.mixed_data = np.array([5.0, 10.0, 35.0, 20.0, -5.0])
        self.with_nans = np.array([5.0, 10.0, np.nan, 20.0, 25.0])

    def test_all_good_data(self):
        """Test data all within range."""
        flags = ctd_qc.range_check(self.good_data, min_val=0, max_val=30)
        np.testing.assert_array_equal(flags, np.ones(5, dtype=int))

    def test_bad_data_flagged(self):
        """Test data outside range is flagged."""
        flags = ctd_qc.range_check(self.mixed_data, min_val=0, max_val=30)
        self.assertEqual(flags[2], 4)  # 35 is out of range
        self.assertEqual(flags[4], 4)  # -5 is out of range
        self.assertEqual(flags[0], 1)  # 5 is good
        self.assertEqual(flags[1], 1)  # 10 is good
        self.assertEqual(flags[3], 1)  # 20 is good

    def test_nan_flagged(self):
        """Test NaN values are flagged as missing."""
        flags = ctd_qc.range_check(self.with_nans, min_val=0, max_val=30)
        self.assertEqual(flags[2], 9)  # NaN should be flagged as 9

    def test_pandas_series_input(self):
        """Test function works with pandas Series."""
        series = pd.Series(self.good_data)
        flags = ctd_qc.range_check(series, min_val=0, max_val=30)
        np.testing.assert_array_equal(flags, np.ones(5, dtype=int))

    def test_custom_flags(self):
        """Test custom QC flag values."""
        flags = ctd_qc.range_check(
            self.mixed_data,
            min_val=0,
            max_val=30,
            flag_bad=3,  # Changed from default 4
            flag_good=2,  # Changed from default 1
        )
        self.assertEqual(flags[0], 2)  # Good should be 2
        self.assertEqual(flags[2], 3)  # Bad should be 3


class TestSpikeDetection(unittest.TestCase):
    """Tests for spike_detection function."""

    def setUp(self):
        """Set up test data."""
        self.clean_data = np.array([5.0, 5.1, 5.0, 5.1, 5.0])
        self.with_spike = np.array([5.0, 5.1, 5.0, 20.0, 5.1, 5.0])
        self.with_nan = np.array([5.0, 5.1, np.nan, 5.1, 5.0])

    def test_clean_data_no_spikes(self):
        """Test clean data is flagged as good."""
        flags = ctd_qc.spike_detection(self.clean_data, threshold=3.0)
        # All non-NaN data should be flagged as 1 (good) or 3 (questionable)
        # Spikes should have flag 4
        self.assertFalse(np.any(flags == 4))

    def test_spike_detected_stddev(self):
        """Test spike detection with standard deviation method."""
        flags = ctd_qc.spike_detection(
            self.with_spike,
            threshold=3.0,
            method="stddev",
        )
        spike_indices = np.where(flags == 4)[0]
        # Index 3 (value 20.0) should be detected as spike
        self.assertIn(3, spike_indices)

    def test_invalid_method(self):
        """Test invalid method raises ValueError."""
        with self.assertRaises(ValueError):
            ctd_qc.spike_detection(self.clean_data, method="invalid")

    def test_nan_handling(self):
        """Test NaN values are flagged as 9."""
        flags = ctd_qc.spike_detection(self.with_nan, threshold=3.0)
        self.assertEqual(flags[2], 9)


class TestRateOfChangeCheck(unittest.TestCase):
    """Tests for rate_of_change_check function."""

    def setUp(self):
        """Set up test data."""
        self.smooth_data = np.array([5.0, 5.1, 5.2, 5.3, 5.4])
        self.with_jump = np.array([5.0, 5.1, 5.2, 10.0, 5.3])  # Jump at index 3

    def test_smooth_data(self):
        """Test smooth data passes check."""
        flags = ctd_qc.rate_of_change_check(self.smooth_data, max_rate=0.5)
        # Should mostly be flagged as good (1), except possible first point
        self.assertTrue(np.all((flags == 1) | (flags == 3)))

    def test_jump_detected(self):
        """Test large jump is detected."""
        flags = ctd_qc.rate_of_change_check(
            self.with_jump,
            max_rate=0.5,
            flag_questionable=3,
        )
        # The jump from 5.2 to 10.0 (difference=4.8) should be flagged
        self.assertEqual(flags[3], 3)

    def test_pandas_series(self):
        """Test with pandas Series."""
        series = pd.Series(self.smooth_data)
        flags = ctd_qc.rate_of_change_check(series, max_rate=0.5)
        self.assertEqual(len(flags), len(series))


class TestApplyAllChecks(unittest.TestCase):
    """Tests for apply_all_checks function."""

    def setUp(self):
        """Set up test data."""
        self.data = pd.DataFrame({
            "temperature": [5.0, 5.1, 5.2, 25.0, 5.3],
            "salinity": [32.0, 32.05, 32.1, 32.5, 32.15],
        })
        self.ranges = {
            "temperature": (-2, 30),
            "salinity": (0, 40),
        }

    def test_range_checks_applied(self):
        """Test range checks are applied to all parameters."""
        flags = ctd_qc.apply_all_checks(self.data, ranges=self.ranges)
        self.assertIn("temperature_QC", flags.columns)
        self.assertIn("salinity_QC", flags.columns)
        self.assertEqual(len(flags), len(self.data))

    def test_spike_checks_applied(self):
        """Test spike detection is applied."""
        flags = ctd_qc.apply_all_checks(self.data, spike_threshold=3.0)
        # Should have spike_QC columns
        spike_cols = [c for c in flags.columns if "spike" in c]
        self.assertGreater(len(spike_cols), 0)

    def test_rate_of_change_checks(self):
        """Test rate of change checks applied."""
        max_rate = {"temperature": 0.5, "salinity": 0.1}
        flags = ctd_qc.apply_all_checks(self.data, max_rate=max_rate)
        self.assertIn("temperature_rate_QC", flags.columns)
        self.assertIn("salinity_rate_QC", flags.columns)

    def test_all_checks_combined(self):
        """Test all checks applied simultaneously."""
        max_rate = {"temperature": 0.5, "salinity": 0.1}
        flags = ctd_qc.apply_all_checks(
            self.data,
            ranges=self.ranges,
            spike_threshold=3.0,
            max_rate=max_rate,
        )
        # Should have multiple QC columns
        self.assertGreater(len(flags.columns), 2)


class TestQCIntegration(unittest.TestCase):
    """Integration tests for QC module."""

    def test_realistic_oceanographic_data(self):
        """Test with realistic oceanographic data."""
        # Create realistic mooring data
        n_samples = 1000
        time_idx = pd.date_range("2024-01-01", periods=n_samples, freq="H")
        
        # Temperature with some daily cycle
        temp_base = 10 + 3 * np.sin(np.arange(n_samples) * 2 * np.pi / 24)
        temperature = temp_base + 0.5 * np.random.normal(0, 1, n_samples)
        
        # Add some anomalies
        temperature[100:105] = 50  # Sensor malfunction
        temperature[500] = -500  # Bad value
        temperature[750] = np.nan  # Missing
        
        data = pd.DataFrame({
            "temperature": temperature,
        }, index=time_idx)
        
        # Apply QC checks
        flags = ctd_qc.apply_all_checks(
            data,
            ranges={"temperature": (-5, 35)},
            spike_threshold=3.0,
        )
        
        # Verify structure
        self.assertEqual(len(flags), len(data))
        self.assertGreater(len(flags.columns), 0)
        
        # Verify bad data is flagged
        # Spike QC or range QC should catch the anomalies
        self.assertGreater((flags >= 3).any(axis=1).sum(), 0)


if __name__ == "__main__":
    unittest.main()
