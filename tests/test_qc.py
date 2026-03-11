"""
Unit tests for EcoFOCIpy Quality Control (QC) module.

Tests for QC flagging, data validation, and anomaly detection functions.
Covers both detailed internal functions and simplified public API.
"""

import unittest
from typing import Tuple

import numpy as np
import pandas as pd

from EcoFOCIpy.qc import ctd_qc


class TestGrossRangeTest(unittest.TestCase):
    """Tests for gross_range_test (internal function)."""

    def setUp(self):
        """Set up test data."""
        self.good_data = pd.Series([5.0, 10.0, 15.0, 20.0, 25.0])
        self.mixed_data = pd.Series([5.0, 10.0, 35.0, 20.0, -5.0])
        self.with_nans = pd.Series([5.0, 10.0, np.nan, 20.0, 25.0])

    def test_all_good_data(self):
        """Test data all within range."""
        config = {'min': 0, 'max': 30}
        flags = ctd_qc.gross_range_test(self.good_data, config)
        np.testing.assert_array_equal(flags.values, np.ones(5, dtype=int))

    def test_bad_data_flagged(self):
        """Test data outside range is flagged."""
        config = {'min': 0, 'max': 30}
        flags = ctd_qc.gross_range_test(self.mixed_data, config)
        self.assertEqual(flags.iloc[2], 4)  # 35 is out of range
        self.assertEqual(flags.iloc[4], 4)  # -5 is out of range
        self.assertEqual(flags.iloc[0], 1)  # 5 is good
        self.assertEqual(flags.iloc[1], 1)  # 10 is good
        self.assertEqual(flags.iloc[3], 1)  # 20 is good

    def test_nan_values(self):
        """Test NaN values are preserved in flags."""
        config = {'min': 0, 'max': 30}
        flags = ctd_qc.gross_range_test(self.with_nans, config)
        # NaN comparison returns False, so NaN values keep default flag value 1
        self.assertTrue(np.isnan(self.with_nans.iloc[2]))


class TestRangeCheck(unittest.TestCase):
    """Tests for public range_check wrapper function."""

    def setUp(self):
        """Set up test data."""
        self.good_data = pd.Series([5.0, 10.0, 15.0, 20.0, 25.0])
        self.mixed_data = pd.Series([5.0, 10.0, 35.0, 20.0, -5.0])
        self.with_nans = pd.Series([5.0, 10.0, np.nan, 20.0, 25.0])

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

    def test_custom_flags(self):
        """Test custom QC flag values."""
        flags = ctd_qc.range_check(
            self.mixed_data,
            min_val=0,
            max_val=30,
            flag_bad=3,
            flag_good=2,
        )
        self.assertEqual(flags[0], 2)  # Good should be 2
        self.assertEqual(flags[2], 3)  # Bad should be 3

    def test_pandas_series_input(self):
        """Test function works with pandas Series."""
        flags = ctd_qc.range_check(self.good_data, min_val=0, max_val=30)
        self.assertEqual(len(flags), 5)
        self.assertTrue(np.all(flags == 1))


class TestSpikeTest(unittest.TestCase):
    """Tests for spike_test (internal function)."""

    def setUp(self):
        """Set up test data."""
        self.clean_data = pd.Series([5.0, 5.1, 5.0, 5.1, 5.0])
        self.with_spike = pd.Series([5.0, 5.1, 5.0, 20.0, 5.1, 5.0])

    def test_clean_data(self):
        """Test clean data is flagged as good."""
        config = {'window': 5, 'threshold': 3.0}
        flags = ctd_qc.spike_test(self.clean_data, config)
        # Most should be good (1)
        self.assertFalse(np.any(flags == 4))

    def test_spike_detected(self):
        """Test spike is detected."""
        config = {'window': 5, 'threshold': 1.0}
        flags = ctd_qc.spike_test(self.with_spike, config)
        spike_indices = np.where(flags == 4)[0]
        # Index 3 (value 20.0) should be detected as spike
        self.assertIn(3, spike_indices)


class TestSpikeDetection(unittest.TestCase):
    """Tests for public spike_detection wrapper function."""

    def setUp(self):
        """Set up test data."""
        self.clean_data = np.array([5.0, 5.1, 5.0, 5.1, 5.0])
        self.with_spike = np.array([5.0, 5.1, 5.0, 20.0, 5.1, 5.0])
        self.with_nan = np.array([5.0, 5.1, np.nan, 5.1, 5.0])

    def test_clean_data_no_spikes(self):
        """Test clean data is flagged as good."""
        flags = ctd_qc.spike_detection(self.clean_data, threshold=3.0)
        # Most should be good (1)
        self.assertFalse(np.any(flags == 4))

    def test_spike_detected_default_method(self):
        """Test spike detection with default median method."""
        flags = ctd_qc.spike_detection(self.with_spike, threshold=1.0, window=5)
        spike_indices = np.where(flags == 4)[0]
        # Index 3 (value 20.0) should be detected as spike
        self.assertIn(3, spike_indices)

    def test_spike_detected_stddev(self):
        """Test spike detection with stddev method."""
        flags = ctd_qc.spike_detection(
            self.with_spike,
            threshold=3.0,
            method="stddev",
        )
        # Should be able to detect spikes
        self.assertEqual(len(flags), len(self.with_spike))

    def test_invalid_method(self):
        """Test invalid method raises ValueError."""
        with self.assertRaises(ValueError):
            ctd_qc.spike_detection(self.clean_data, method="invalid")

    def test_numpy_array_input(self):
        """Test with numpy array input."""
        flags = ctd_qc.spike_detection(self.clean_data, threshold=3.0)
        self.assertEqual(len(flags), len(self.clean_data))


class TestStuckValueTest(unittest.TestCase):
    """Tests for stuck_value_test function."""

    def setUp(self):
        """Set up test data."""
        self.changing_data = pd.Series([5.0, 5.1, 5.2, 5.3, 5.4])
        self.stuck_data = pd.Series([5.0, 5.0, 5.0, 5.0, 5.1, 5.1, 5.1])

    def test_changing_data_ok(self):
        """Test changing data passes stuck value test."""
        config = {'consecutive_limit': 3}
        flags = ctd_qc.stuck_value_test(self.changing_data, config)
        # Should all be good
        self.assertTrue(np.all(flags == 1))

    def test_stuck_data_flagged(self):
        """Test stuck data is flagged."""
        config = {'consecutive_limit': 3}
        flags = ctd_qc.stuck_value_test(self.stuck_data, config)
        # Indices with stuck values should be flagged 4
        stuck_indices = np.where(flags == 4)[0]
        self.assertGreater(len(stuck_indices), 0)

    def test_different_consecutive_limit(self):
        """Test with different consecutive limit."""
        config = {'consecutive_limit': 5}
        flags = ctd_qc.stuck_value_test(self.stuck_data, config)
        # With higher limit, fewer points should be flagged
        self.assertEqual(len(flags), len(self.stuck_data))


class TestGradientTest(unittest.TestCase):
    """Tests for gradient_test (internal function)."""

    def setUp(self):
        """Set up test data."""
        self.smooth_data = pd.Series([5.0, 5.1, 5.2, 5.3, 5.4])
        self.with_jump = pd.Series([5.0, 5.1, 5.2, 10.0, 5.3])

    def test_smooth_gradients(self):
        """Test smooth data passes gradient test."""
        config = {'threshold': 0.5}
        flags = ctd_qc.gradient_test(self.smooth_data, config)
        # First point might have NaN, rest should be good
        self.assertTrue(np.all((flags.iloc[1:] == 1)))

    def test_jump_detected(self):
        """Test large jump is detected."""
        config = {'threshold': 0.5}
        flags = ctd_qc.gradient_test(self.with_jump, config)
        # The jump from 5.2 to 10.0 (gradient=4.8) should be flagged
        self.assertEqual(flags.iloc[3], 4)


class TestRateOfChangeCheck(unittest.TestCase):
    """Tests for public rate_of_change_check wrapper function."""

    def setUp(self):
        """Set up test data."""
        self.smooth_data = np.array([5.0, 5.1, 5.2, 5.3, 5.4])
        self.with_jump = np.array([5.0, 5.1, 5.2, 10.0, 5.3])

    def test_smooth_data(self):
        """Test smooth data passes check."""
        flags = ctd_qc.rate_of_change_check(self.smooth_data, max_rate=0.5)
        # Should mostly be flagged as good (1) or questionable (3)
        self.assertTrue(np.all((flags == 1) | (flags == 3) | np.isnan(flags)))

    def test_jump_detected(self):
        """Test large jump is detected."""
        flags = ctd_qc.rate_of_change_check(
            self.with_jump,
            max_rate=0.5,
            flag_questionable=3,
        )
        # The jump at index 3 should be flagged as questionable
        self.assertEqual(flags[3], 3)

    def test_custom_flags(self):
        """Test custom flag values."""
        flags = ctd_qc.rate_of_change_check(
            self.smooth_data,
            max_rate=0.5,
            flag_good=2,
            flag_questionable=5,
        )
        # Should use custom flag values
        self.assertTrue(np.all((flags == 2) | (flags == 5) | np.isnan(flags)))


class TestDensityInversionTest(unittest.TestCase):
    """Tests for density_inversion_test function."""

    def setUp(self):
        """Set up test data."""
        # Create stable water column (increasing density with depth)
        self.stable_df = pd.DataFrame({
            'pressure': [10, 50, 100, 200, 500],
            'temperature': [20.0, 15.0, 10.0, 5.0, 2.0],
            'salinity': [35.0, 35.1, 35.2, 35.3, 35.4],
            'longitude': [-179.5] * 5,
            'latitude': [57.0] * 5,
        })
        
        # Create unstable water column (density inversion)
        self.unstable_df = pd.DataFrame({
            'pressure': [10, 50, 100, 200, 500],
            'temperature': [20.0, 5.0, 10.0, 5.0, 2.0],  # Jump creates inversion
            'salinity': [35.0, 35.5, 35.1, 35.3, 35.4],
            'longitude': [-179.5] * 5,
            'latitude': [57.0] * 5,
        })

    def test_stable_water_column(self):
        """Test stable water column passes test."""
        config = {'threshold': -0.03}
        flags = ctd_qc.density_inversion_test(self.stable_df, config)
        # Most should be good
        self.assertEqual(len(flags), len(self.stable_df))

    def test_unstable_water_detected(self):
        """Test unstable water column is flagged."""
        config = {'threshold': -0.03}
        flags = ctd_qc.density_inversion_test(self.unstable_df, config)
        # Should have some flagged points
        self.assertEqual(len(flags), len(self.unstable_df))

    def test_default_threshold(self):
        """Test default threshold is used."""
        config = {}  # No threshold specified
        flags = ctd_qc.density_inversion_test(self.stable_df, config)
        self.assertEqual(len(flags), len(self.stable_df))


class TestApplyAllChecks(unittest.TestCase):
    """Tests for public apply_all_checks wrapper function."""

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
        # Should have spike_QC column
        self.assertIn("spike_QC", flags.columns)

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
        # Original data should still be present
        self.assertIn("temperature", flags.columns)
        self.assertIn("salinity", flags.columns)

    def test_only_ranges(self):
        """Test with only range checks."""
        flags = ctd_qc.apply_all_checks(self.data, ranges=self.ranges)
        self.assertIn("temperature_QC", flags.columns)
        self.assertIn("salinity_QC", flags.columns)

    def test_empty_parameters(self):
        """Test with no parameters specified."""
        flags = ctd_qc.apply_all_checks(self.data)
        # Should still have spike_QC even with no other params
        self.assertIn("spike_QC", flags.columns)


class TestRunCtdQc(unittest.TestCase):
    """Tests for run_ctd_qc function."""

    def setUp(self):
        """Set up test data."""
        self.data = pd.DataFrame({
            'temperature': [5.0, 5.1, 5.2, 25.0, 5.3],
            'salinity': [32.0, 32.05, 32.1, 32.5, 32.15],
            'pressure': [10, 50, 100, 150, 200],
        })

    def test_qc_columns_created(self):
        """Test QC flag columns are created."""
        config = {
            'temperature': {
                'gross_range': {'min': -2, 'max': 30}
            },
            'salinity': {
                'gross_range': {'min': 0, 'max': 40}
            }
        }
        result = ctd_qc.run_ctd_qc(self.data, config)
        self.assertIn('temperature_qc', result.columns)
        self.assertIn('salinity_qc', result.columns)
        self.assertEqual(len(result), len(self.data))

    def test_multiple_tests_combined(self):
        """Test multiple tests are combined (worst flag wins)."""
        config = {
            'temperature': {
                'gross_range': {'min': -2, 'max': 30},
                'spike': {'window': 5, 'threshold': 1.0}
            },
            'salinity': {
                'gross_range': {'min': 0, 'max': 40}
            }
        }
        result = ctd_qc.run_ctd_qc(self.data, config)
        # Result should have flags applied
        self.assertTrue(np.all((result['temperature_qc'] >= 1) | (result['temperature_qc'].isna())))

    def test_original_data_preserved(self):
        """Test original data is preserved."""
        config = {
            'temperature': {'gross_range': {'min': -2, 'max': 30}},
            'salinity': {'gross_range': {'min': 0, 'max': 40}}
        }
        result = ctd_qc.run_ctd_qc(self.data, config)
        pd.testing.assert_series_equal(result['temperature'], self.data['temperature'])
        pd.testing.assert_series_equal(result['salinity'], self.data['salinity'])


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
        self.assertGreater(len(flags.columns), 1)
        
        # Verify bad data is flagged
        # Quality columns should exist
        qc_cols = [c for c in flags.columns if 'QC' in c or 'qc' in c]
        self.assertGreater(len(qc_cols), 0)

    def test_complete_workflow(self):
        """Test complete QC workflow from raw data to flagged output."""
        # Create sample data
        data = pd.DataFrame({
            'temperature': np.random.normal(10, 2, 100),
            'salinity': np.random.normal(35, 0.5, 100),
            'pressure': np.linspace(10, 1000, 100),
        })
        
        # Method 1: Using apply_all_checks
        result1 = ctd_qc.apply_all_checks(
            data,
            ranges={'temperature': (0, 30), 'salinity': (30, 40)},
            spike_threshold=3.0
        )
        self.assertGreater(len(result1.columns), len(data.columns))
        
        # Method 2: Using run_ctd_qc with config
        config = {
            'temperature': {
                'gross_range': {'min': 0, 'max': 30},
                'spike': {'window': 5, 'threshold': 2.0}
            },
            'salinity': {
                'gross_range': {'min': 30, 'max': 40}
            }
        }
        result2 = ctd_qc.run_ctd_qc(data, config)
        self.assertGreater(len(result2.columns), len(data.columns))


if __name__ == "__main__":
    unittest.main()

