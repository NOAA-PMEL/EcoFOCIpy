import pytest
import pandas as pd
import os
from EcoFOCIpy.io.prooceanus_parser import tdgp  # Import your class


@pytest.fixture
def mock_files():
    """Pytest fixture to create mock data files for testing."""
    good_file_path = 'test_good_data.txt'
    bad_start_file_path = 'test_bad_start.txt'

    # Create a perfectly formatted mock data file
    with open(good_file_path, 'w') as f:
        f.write("Header Line 1\n")
        f.write("File Contents:\n")
        f.write("Year,Month,Day,Hour,Minute,Second,Pressure,Temp\n")
        f.write("\n")
        f.write("2024,7,9,10,0,0,101.3,25.1\n")
        f.write("2024,7,9,10,1,0,101.4,25.2\n")
        f.write("Finished: 2 records\n")

    # Create a file missing the start marker
    with open(bad_start_file_path, 'w') as f:
        f.write("Header Line 1\n")
        f.write("Year,Month,Day,Hour,Minute,Second,Pressure,Temp\n")
        f.write("2024,7,9,10,0,0,101.3,25.1\n")
        f.write("Finished: 1 record\n")

    # 'yield' passes these names to the test function
    yield good_file_path, bad_start_file_path

    # Cleanup: code after 'yield' runs after the test is complete
    print("\nCleaning up mock files...")
    os.remove(good_file_path)
    os.remove(bad_start_file_path)


def test_successful_parsing(mock_files):
    """Test parsing a well-formed file."""
    good_file, _ = mock_files  # Unpack file paths from the fixture
    parser = tdgp()
    df, header = parser.parse(good_file)

    # Assertions are simpler with pytest
    assert df.shape == (2, 2)
    assert df.columns.tolist() == ['Pressure', 'Temp']
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df['Pressure'].iloc[1] == 101.4
    assert len(header) == 2
    assert "File Contents:" in header[1]


def test_file_not_found():
    """Test that FileNotFoundError is raised for a non-existent file."""
    parser = tdgp()
    with pytest.raises(FileNotFoundError):
        parser.parse('non_existent_file.txt')


def test_missing_start_marker(mock_files):
    """Test that ValueError is raised if 'File Contents:' is missing."""
    _, bad_file = mock_files  # Get the bad file path
    parser = tdgp()
    with pytest.raises(ValueError, match="Could not find data markers"):
        parser.parse(bad_file)

# dropped datetime_index=False tests
