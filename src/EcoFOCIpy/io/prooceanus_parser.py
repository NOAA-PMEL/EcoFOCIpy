# EcoFOCI
"""Contains a collection of pro-oceanus equipment parsing.
(A seabird product now)

These include:

TDGP - moored

Non-moored:
* processing is likely the same if recording internally.

code-refactor suggestsion from Gemini
"""
import pandas as pd
import io
from typing import List, Tuple, Optional


class tdgp(object):
    r"""
    A parser for Pro-Oceanus TDGP (Total Dissolved Gas Pressure) data files.

    This class reads a TDGP text file, extracts the header and data,
    and returns them as a pandas DataFrame.

    Attributes:
        rawdata_df (pd.DataFrame): The parsed data stored in a DataFrame.
                                   This is populated after calling the parse() method.
    """
    def __init__(self):
        """Initializes the tdgp parser."""
        self.rawdata_df: Optional[pd.DataFrame] = None


    def parse(self, filename: str, datetime_index: bool = True) -> Tuple[pd.DataFrame, List[str]]:
        r"""
        Opens and reads a TDGP text file.

        The method locates the data block within the file, which is expected
        to be between a "File Contents:" line and a "Finished" line.

        Args:
            filename (str): The full path to the TDGP .txt file.
            datetime_index (bool): If True, sets a DatetimeIndex for the DataFrame
                                   and removes the original date/time columns.

        Returns:
            Tuple[pd.DataFrame, List[str]]: A tuple containing:
                - A pandas DataFrame with the parsed data.
                - A list of strings representing the file's header.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the start or end markers for the data block
                        are not found in the file.
        """

        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: The file {filename} was not found.")
            raise

        # Find the start and end of the data block
        try:
            start_marker = "File Contents:"
            end_marker = "Finished"

            start_index = next(i for i, line in enumerate(lines) if start_marker in line)
            end_index = next(i for i, line in enumerate(lines) if end_marker in line)

        except StopIteration:
            raise ValueError(
                f"Could not find data markers ('{start_marker}', '{end_marker}') in the file."
            )

        # Extract header, column names, and data lines
        header = lines[:start_index + 1]
        column_names = lines[start_index + 1].strip().split(',')
        data_lines = lines[start_index + 3:end_index]

        # Use io.StringIO to treat our list of strings as a file for pandas
        data_io = io.StringIO(''.join(data_lines))

        rawdata_df = pd.read_csv(
            data_io,
            delimiter=r"\s|,",
            names=column_names,
            engine='python'  # Use the faster C engine
        )

        # Efficiently create the datetime column
        # This is significantly faster than concatenating strings row-by-row
        date_cols = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Second']
        rawdata_df['date_time'] = pd.to_datetime(rawdata_df[date_cols])

        if datetime_index:
            rawdata_df = rawdata_df.set_index('date_time').drop(columns=date_cols)

        self.rawdata_df = rawdata_df

        return (rawdata_df, header)
