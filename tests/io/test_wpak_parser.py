import pytest
import pandas as pd
import os
from EcoFOCIpy.io.wpak_parser import wpak  # Import the class from your script


@pytest.fixture
def mock_wpak_file():
    """Pytest fixture to create a temporary WPAK data file for testing."""
    file_path = 'test_wpak_data.txt'
    # Mock data mimicking the expected format
    file_content = """datestr      timestr      col1   col2
25/07/10   06:30:00   10.1   20.2
25/07/10   06:30:05   10.2   20.3
25/07/10   06:30:10   10.3   20.4
"""
    with open(file_path, 'w') as f:
        f.write(file_content)

    # 'yield' provides the file path to the test function
    yield file_path

    # This code runs after the test is complete to clean up
    os.remove(file_path)

# Test Functions

def test_successful_parsing(mock_wpak_file):
    """Tests that a correctly formatted file is parsed successfully."""
    parser = wpak()
    df = parser.parse(mock_wpak_file)
    
    # Verify the DataFrame's properties
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 2) # 3 rows, 2 data columns
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.columns.tolist() == ['col1', 'col2']
    
    # Check a specific data point
    assert df['col2'].iloc[1] == 20.3


def test_file_not_found():
    """Tests that FileNotFoundError is raised for a non-existent file."""
    parser = wpak()
    with pytest.raises(FileNotFoundError):
        parser.parse(filename="non_existent_file.txt")


def test_datetime_index_false(mock_wpak_file):
    """Tests the behavior when datetime_index is set to False."""
    parser = wpak()
    df = parser.parse(mock_wpak_file, datetime_index=False)


    # Check that the original and new datetime columns exist
    expected_cols = ['datestr', 'timestr', 'col1', 'col2', 'date_time']
    assert df.columns.tolist() == expected_cols
    assert 'date_time' in df
    assert isinstance(df.index, pd.RangeIndex)