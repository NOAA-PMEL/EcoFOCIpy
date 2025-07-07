import numpy as np
import pytest
from EcoFOCIpy.math.lanzcos import lanzcos, low_pass_weights, spectral_filtering, spectral_window


# Helper function to create simple sine waves for testing
def create_sine_wave(frequency, sampling_rate, duration):
    t = np.arange(0, duration, 1/sampling_rate)
    return np.sin(2 * np.pi * frequency * t)


# Test for low_pass_weights
def test_low_pass_weights_basic():
    window = 121
    cutoff = 0.1
    weights = low_pass_weights(window, cutoff)
    assert isinstance(weights, np.ndarray)
    assert len(weights) == window - 1 # (2 * ((121 - 1) // 2) + 1) - 2 = 121 - 2 = 119
    # Check for symmetry (approximate due to floating point)
    assert np.allclose(weights[:len(weights)//2], weights[len(weights)//2:][::-1])
    # Check that the sum of weights is close to 2*cutoff, a property of Lanczos weights
    assert np.isclose(np.sum(weights), 2 * cutoff, atol=1e-5) # Sum of sinc function should be 1, but here it's 2*cutoff at origin, then sums of parts


def test_low_pass_weights_small_window():
    window = 3
    cutoff = 0.2
    weights = low_pass_weights(window, cutoff)
    assert isinstance(weights, np.ndarray)
    assert len(weights) == window - 1 # (2 * ((3 - 1) // 2) + 1) - 2 = 3 - 2 = 1
    # For window = 3, only the center weight is returned after slicing
    assert len(weights) == 2 # 2*order+1 = 2*2+1 = 5. w[1:-1] means 3 weights


def test_low_pass_weights_different_cutoff():
    window = 21
    cutoff_high = 0.4
    cutoff_low = 0.05
    weights_high = low_pass_weights(window, cutoff_high)
    weights_low = low_pass_weights(window, cutoff_low)
    assert np.sum(weights_high) > np.sum(weights_low) # Higher cutoff means larger sum of weights (more "pass-through")


# Test for spectral_window
def test_spectral_window_basic():
    weights = low_pass_weights(21, 0.1)
    n = 100
    window, Ff = spectral_window(weights, n)
    assert isinstance(window, np.ndarray)
    assert isinstance(Ff, np.ndarray)
    assert len(window) == len(Ff)
    assert Ff[0] == 0.0
    assert Ff[-1] == 1.0 or np.isclose(Ff[-1], 1.0) # Due to the append logic for even n


def test_spectral_window_n_even_odd():
    weights = low_pass_weights(21, 0.1)
    n_even = 100
    _, Ff_even = spectral_window(weights, n_even)
    assert np.isclose(Ff_even[-1], 1.0)

    n_odd = 101
    _, Ff_odd = spectral_window(weights, n_odd)
    assert not np.isclose(Ff_odd[-1], 1.0) # Should be 1.0 - 2/N for odd N unless n is small


# Test for spectral_filtering
def test_spectral_filtering_basic_low_pass():
    # Create a signal with low and high frequencies
    sampling_rate = 100 # Hz
    duration = 1 # seconds
    low_freq = 5 # Hz
    high_freq = 40 # Hz
    data = create_sine_wave(low_freq, sampling_rate, duration) + \
           create_sine_wave(high_freq, sampling_rate, duration)

    # Design a low-pass window that cuts off the high frequency
    window_length = len(data) // 2 + 1 # Matching the expected length for CxH
    # Simple rectangular window for testing purposes (conceptually)
    # In a real scenario, you'd use the output of spectral_window
    test_window = np.ones(window_length)
    cutoff_index = int(window_length * (high_freq - 5) / (sampling_rate / 2)) # Adjust cutoff
    test_window[cutoff_index:] = 0 # Set high frequencies to zero

    filtered_data, Cx = spectral_filtering(data, test_window)

    assert isinstance(filtered_data, np.ndarray)
    assert len(filtered_data) == len(data)

    # Verify that high frequencies are attenuated in the output
    # This is a qualitative test; a quantitative test would involve checking FFT magnitudes
    # For now, we'll check if the amplitude of the filtered signal is closer to the low-frequency component
    amplitude_original = np.max(data) - np.min(data)
    amplitude_filtered = np.max(filtered_data) - np.min(filtered_data)

    # The amplitude of the filtered signal should be significantly less than the original,
    # as the high frequency component has been removed.
    assert amplitude_filtered < amplitude_original * 0.8 # Heuristic check


def test_spectral_filtering_empty_input():
    x = np.array([])
    window = np.array([])
    with pytest.raises(ValueError, match="empty sequence"):
        spectral_filtering(x, window)


def test_spectral_filtering_single_point_input():
    x = np.array([1.0])
    window = np.array([1.0]) # Must be at least length 1 for basic ops
    # The FFT of a single point is just the point itself.
    # The window operation will be element-wise.
    # Inverse FFT of a single point (after conj and append) should be the original point.
    y, Cx = spectral_filtering(x, window)
    assert np.isclose(y[0], x[0])


# Test for lanzcos
def test_lanzcos_basic_filtering_effect():
    # Create hourly data: a slow oscillation + a fast oscillation
    # dt = 1.0 (hourly data)
    # Cf = 35 hours (cutoff period)
    # Nyquist frequency Nf = 1 / (2 * (1 * 24)) = 1 / 48 cycles/hour

    # Slow oscillation: period = 100 hours (freq = 0.01 cycles/hour) - should pass
    # Fast oscillation: period = 10 hours (freq = 0.1 cycles/hour) - should be attenuated by Cf=35
    # Cf = 35 hours means cutoff frequency is 1/35 cycles/hour approx 0.028 cycles/hour

    time_points = 24 * 100 # 100 days of hourly data
    t = np.arange(time_points) # Assuming dt=1 hour implicitly

    slow_oscillation = np.sin(2 * np.pi * t / 100.0) # Period 100 hours
    fast_oscillation = np.sin(2 * np.pi * t / 10.0)  # Period 10 hours

    data = slow_oscillation + fast_oscillation
    dt = 1.0 # hourly data
    Cf = 35.0 # cutoff period in hours

    filtered_data = lanzcos(data, dt, Cf)

    assert isinstance(filtered_data, np.ndarray)
    assert len(filtered_data) == len(data)

    # Qualitatively check that the amplitude of the fast oscillation is reduced
    # A more robust test would involve FFT of original and filtered data
    # and comparing magnitudes at specific frequencies.
    
    # Calculate variance to see reduction in high-frequency content
    original_variance = np.var(data)
    filtered_variance = np.var(filtered_data)

    # The filtered data's variance should be significantly lower than the original's,
    # as the high-frequency component contributes to the variance.
    assert filtered_variance < original_variance * 0.8 # Heuristic check

    # Check that the low-frequency component is largely preserved
    # This is a bit harder without proper spectral analysis in the test.
    # One way is to compare peaks or overall shape.
    # For now, let's just assert that it's not zeroed out completely.
    assert np.max(np.abs(filtered_data)) > 0.1 * np.max(np.abs(slow_oscillation)) # Should retain some amplitude


def test_lanzcos_empty_data():
    data = np.array([])
    dt = 1.0
    Cf = 35.0
    # Expect error from numpy.fft.fft if input is empty
    with pytest.raises(ValueError, match="empty sequence"):
        lanzcos(data, dt, Cf)


def test_lanzcos_single_point_data():
    data = np.array([10.0])
    dt = 1.0
    Cf = 35.0
    # For a single point, FFT is just the point. Filtering should return the point itself.
    filtered_data = lanzcos(data, dt, Cf)
    assert isinstance(filtered_data, np.ndarray)
    assert len(filtered_data) == len(data)
    assert np.isclose(filtered_data[0], data[0])

    
def test_lanzcos_different_dt():
    # Test with dt that is not 1.0 (e.g., daily data, dt=24.0)
    time_points = 100
    t = np.arange(time_points)
    data = np.sin(2 * np.pi * t / 5.0) + np.sin(2 * np.pi * t / 50.0)  # 5 and 50 days period

    dt = 24.0  # daily data, so 1 time step is 24 hours
    # If Cf = 35, it's 35 hours. So for daily data, it's 35/24 days.
    # This means a period of 5 days (120 hours) should pass, 50 days should pass.
    # If we filter at 35 hours, frequencies faster than 1/35 cycles/hour should be removed.
    # For daily data, a 5-day period is 1/5 cycles/day = 1/ (5*24) cycles/hour = 1/120 cycles/hour.
    # A 50-day period is 1/50 cycles/day = 1/(50*24) cycles/hour = 1/1200 cycles/hour.
    # Both are much slower than 1/35 cycles/hour. So both should pass.
    # This test is more about ensuring the `dt` calculation in `lanzcos` is correct.

    Cf = 35.0  # cutoff period in hours


    filtered_data = lanzcos(data, dt, Cf)

    assert isinstance(filtered_data, np.ndarray)
    assert len(filtered_data) == len(data)

    # In this scenario, with Cf=35 hours and dt=24 hours, both components
    # (5-day and 50-day period) are much longer than 35 hours.
    # Thus, the filtering should be minimal, and the output should be very close to the input.
    assert np.allclose(data, filtered_data, atol=1e-2)

