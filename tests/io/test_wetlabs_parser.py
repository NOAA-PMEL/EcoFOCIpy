import pytest
import pandas as pd
import numpy as np
import os
from EcoFOCIpy.io.wetlabs_parser import wetlabs # Import your class

# Define a fixture to create mock data files for tests
@pytest.fixture
def mock_file():
    """Pytest fixture to create a mock data file for testing."""
    good_file_path = 'test_good_data.txt'
    with open(good_file_path, 'w') as f:
        f.write("Some header info\n")
        f.write("More header info\n")
        f.write("$get\n")  # The critical header marker
        f.write("some line\n")
        f.write("07/09/25 10:00:00 700 137 532 4182 173\n")
        f.write("07/09/25 10:00:01 700 139 532 4190 174\n")
        f.write("07/09/25 10:00:02 700 142 532 4195 175\n")
        
    # 'yield' passes the file path to the test function
    yield good_file_path
    
    # Cleanup: code after 'yield' runs after the test is complete
    os.remove(good_file_path)

## Test Suite
### 1. Parsing Tests

def test_successful_parsing(mock_file):
    """Test parsing a well-formed file with 2 channels."""
    parser = wetlabs()
    df, header = parser.parse(mock_file)

    # Check DataFrame shape, columns, and index
    assert df.shape == (3, 3) # 3 rows, 3 data columns ('700', '532', 'TempCount')
    assert df.columns.tolist() == ['700', '532', 'TempCount']
    assert isinstance(df.index, pd.DatetimeIndex)
    
    # Check a specific data point and header content
    assert df['532'].iloc[1] == 4190
    assert len(header) == 3
    assert "$get" in header[2]

def test_parse_raises_file_not_found():
    """Test that FileNotFoundError is raised for a non-existent file."""
    parser = wetlabs()
    with pytest.raises(FileNotFoundError):
        parser.parse('non_existent_file.txt')

def test_parse_raises_value_error_for_bad_format():
    """Test that ValueError is raised for a file with an invalid column count."""
    bad_file_path = 'bad_format.txt'
    with open(bad_file_path, 'w') as f:
        f.write("$get\n\n07/09/25 10:00:00 700 137 532 4182\n") # Missing TempCount col
    
    parser = wetlabs()
    with pytest.raises(ValueError, match="Unrecognized file format"):
        parser.parse(bad_file_path)
    
    os.remove(bad_file_path)

### 2. Data Processing Tests

def test_engr2sci_conversion(mock_file):
    """Test the conversion from engineering counts to scientific units."""
    parser = wetlabs()
    parser.parse(mock_file)

    cal_coefs = {
        '700': {'scaleFactor': 0.012, 'darkCounts': 50, 'outname': 'Chlorophyll'},
        '532': {'scaleFactor': 0.004, 'darkCounts': 48, 'outname': 'Turbidity'}
    }
    
    sci_df = parser.engr2sci(cal_coefs)
    
    # Check that new columns exist
    assert 'Chlorophyll' in sci_df.columns
    assert 'Turbidity' in sci_df.columns
    
    # Verify a calculation
    # For Chlorophyll row 0: 0.012 * (137 - 50) = 1.044
    np.testing.assert_allclose(sci_df['Chlorophyll'].iloc[0], 1.044)

def test_engr2sci_raises_runtime_error_before_parse():
    """Test that calling engr2sci before parsing raises an error."""
    parser = wetlabs()
    with pytest.raises(RuntimeError, match="Data must be parsed"):
        parser.engr2sci({})

### 3. Time Correction Tests

def test_time_correction_offset(mock_file):
    """Test the 'offset_only' time correction method."""
    parser = wetlabs()
    original_df, _ = parser.parse(mock_file)
    original_first_time = original_df.index[0]
    
    # Apply a 1-hour offset
    corrected_df = parser.time_correction(offset_seconds=3600, method='offset_only')
    expected_first_time = original_first_time + pd.Timedelta(seconds=3600)
    
    assert corrected_df.index[0] == expected_first_time

def test_time_correction_linear_methods_match(mock_file):
    """Test that 'linear' and 'linear-gemini' methods produce identical results."""
    # Parser for 'linear' method
    parser1 = wetlabs()
    parser1.parse(mock_file)
    df1 = parser1.time_correction(offset_seconds=100, method='linear')

    # Parser for 'linear-gemini' method
    parser2 = wetlabs()
    parser2.parse(mock_file)
    df2 = parser2.time_correction(offset_seconds=100, method='linear-gemini')

    # The timestamps should be identical
    np.testing.assert_allclose(df1.index.astype(np.int64), df2.index.astype(np.int64))