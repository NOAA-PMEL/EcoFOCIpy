from typing import Optional

import pandas as pd


class wpak(object):
    r"""
    A parser for MetOcean WeatherPak data files.

    This class is designed to read and process data from WPAK instruments,
    handling both standard and ARGOS file formats.

    Todo: WPAK via Argos
    """

    def __init__(self):
        """Initializes the parser instance."""
        self.data: Optional[pd.DataFrame] = None

    def parse(self, filename: str, datetime_index: bool = True) -> pd.DataFrame:
        r"""
        Opens and reads WPAK data files from a given path.

        Args:
            filename (str): The full path to the .csv or .txt data file.
            datetime_index (bool): If True, sets a DatetimeIndex and drops the
                                   original date/time columns.

        Returns:
            A pandas DataFrame containing the parsed data.

        Raises:
            ValueError: If no filename is provided.
            FileNotFoundError: If the specified file does not exist.
        """
        if not filename:
            raise ValueError("A filename must be provided.")

        # The 'delim_whitespace=True' argument is more robust for any
        # amount of space between columns.
        rawdata_df = pd.read_csv(filename, delim_whitespace=True)

        # This is the most efficient way to create a datetime column
        # as it operates on the DataFrame columns directly.
        rawdata_df["date_time"] = pd.to_datetime(
            rawdata_df[["DATE", "TIME"]].astype(str).agg(" ".join, axis=1),
            format="%y/%m/%d %H:%M:%S"
        )

        if datetime_index:
            # Simplified index setting and dropping of original columns
            rawdata_df = rawdata_df.set_index('date_time').drop(columns=['DATE', 'TIME'])

        self.data = rawdata_df
        return self.data
