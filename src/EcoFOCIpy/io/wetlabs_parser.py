# EcoFOCI
"""Contains a collection of wetlabs equipment parsing.
(A seabird product now)

These include:

Moored Eco and Wetstars:
* 1 channel -> 3 channel systems

Non-moored:
* processing is likely the same if recording internally.

Gemini refactor suggestions : 2025
"""
import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


class wetlabs(object):
    r""" Wetlabs Unified parser

    EcoFLS(B) - single channel fluorometer (B-battery pack)
    EcoFLNT(US) - dual channel fluorometer and Turb
    Triplet - three channels
    EcoPAR- single channel PAR sensor

    Eco's have an array of channels to choose from... files are all the same,
    you must provide the right cal coefs for the data

    """
    def __init__(self):
        """data is a pandas dataframe
        Wich is immediatly converted to xarray
        """
        self.rawdata_df: Optional[pd.DataFrame] = None

    def parse(self, filename: str) -> Tuple[pd.DataFrame, List[str]]:
        r"""
        Opens and reads Wetlabs data files.

        The method automatically detects the header, determines the number of sensor
        channels, and structures the data accordingly.

        Args:
            filename (str): The full path to the .cnv file.

        Returns:
            A tuple containing the parsed pandas DataFrame and a list of header strings.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file format is unrecognized or header markers are missing.
        """
        header_lines = []
        header_row_count = 0
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                header_lines.append(line)
                if "$get" in line:
                    header_row_count = i + 2
                    break
            else:
                raise ValueError("Header marker '$get' not found in file.")

        # Read the data section of the file
        rawdata_df = pd.read_csv(filename, delimiter=r'\s+', header=None, skiprows=header_row_count)

        # Programmatically determine number of channels and assign columns
        num_cols = len(rawdata_df.columns)
        if num_cols == 2:
            num_channels = 1 # PAR device
        elif (num_cols - 3) % 2 == 0 and num_cols >= 5:
            num_channels = (num_cols - 3) // 2
        else:
            raise ValueError(f"Unrecognized file format with {num_cols} columns.")

        # Combine date and time columns for the datetime index
        datetime_col = pd.to_datetime(rawdata_df[0] + ' ' + rawdata_df[1], format="%m/%d/%y %H:%M:%S")

        # Build the final DataFrame
        data = {'date_time': datetime_col}
        for i in range(num_channels):
            channel_id_col_index = 2 + (i * 2)
            data_col_index = 3 + (i * 2)
            # Use the first row's channel ID as the column name
            channel_name = str(rawdata_df[channel_id_col_index][0])
            data[channel_name] = rawdata_df[data_col_index]

        data['TempCount'] = rawdata_df[num_cols - 1]

        self.rawdata_df = pd.DataFrame(data).set_index('date_time')
        return self.rawdata_df, header_lines

    def engr2sci(self, cal_coef: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts engineering units (counts) to scientific units.

        Args:
            cal_coef: A dictionary where each key is the channel name (e.g., '700')
                      and the value is another dictionary with 'scaleFactor',
                      'darkCounts', and 'outname' (e.g., 'Chlorophyll').

                      e.g  {channel_name:{scaleF:0,darkCounts:0,outname=None}}
                            where channel_name = wavelength that the column gets
                            labeled. scaleF and darkCounts are wetlabs
                            provided cal coefficients and name is the measurement
                            name (chlor, turb, scatter, CDOM, etc)

        Returns:
            The DataFrame with new columns containing scientific data.
        """
        if self.rawdata_df is None:
            raise RuntimeError("Data must be parsed before calling engr2sci.")

        for channel, coefs in cal_coef.items():
            try:
                out_name = coefs['outname']
                scale_factor = coefs['scaleFactor']
                dark_counts = coefs['darkCounts']
                # Apply the calibration equation
                self.rawdata_df[out_name] = scale_factor * (self.rawdata_df[str(channel)] - dark_counts)
            except KeyError:
                print(f"Warning: Calibration coefficients for channel '{channel}' are missing or incomplete. Skipping.")
            except Exception as e:
                print(f"Warning: Could not process channel '{channel}'. Reason: {e}")
        return self.rawdata_df

    def time_correction(self, offset_seconds: float, method: str = 'offset_only') -> pd.DataFrame:
        """
        Applies a time offset or linear drift correction to the data's index.

        Args:
            offset_seconds: The total time offset in seconds to apply.
            method: 'offset_only' for a simple shift or 'linear' for drift correction.

        Returns:
            The DataFrame with the corrected time index.
        """
        if self.rawdata_df is None:
            raise RuntimeError("Data must be parsed before calling time_correction.")

        if method == 'offset_only':
            self.rawdata_df.index += pd.to_timedelta(offset_seconds, unit='s')
        elif method == 'linear-gemini':
            # Vectorized approach for linear drift correction (much faster than apply) - but gemini induced and
            #  needs to be verified
            start_time = self.rawdata_df.index[0]
            total_duration_seconds = (self.rawdata_df.index[-1] - start_time).total_seconds()

            if total_duration_seconds == 0:  # Avoid division by zero
                return self.rawdata_df

            time_elapsed = (self.rawdata_df.index - start_time).total_seconds()
            correction_factor = time_elapsed / total_duration_seconds
            time_offset = pd.to_timedelta(correction_factor * offset_seconds, unit='s')
            self.rawdata_df.index += time_offset
        elif method == 'linear':
            def lineartimecorr(x, deltaT, T0):
                date = x + pd.Timedelta(seconds=((x - T0).total_seconds() * deltaT))
                return date

            T0 = self.rawdata_df.index[0]

            if T0 == self.rawdata_df.index[-1]:  # Avoid division by zero
                return self.rawdata_df

            deltaT = (datetime.timedelta(seconds=offset_seconds) /
                      (self.rawdata_df.index[-1] - T0))

            self.rawdata_df.index = (self.rawdata_df
                                     .reset_index()
                                     .apply(lambda x: lineartimecorr(x.date_time,
                                            deltaT,
                                            T0),
                                            axis=1
                                            )
                                     )
            self.rawdata_df.index.name = 'date_time'

        else:
            raise ValueError(f"Unknown time correction method: {method}")

        return self.rawdata_df

    def NaT_removal(self) -> pd.DataFrame:
        """
        Removes rows with any NaN values (specifically for NaT values) from the DataFrame.

        Returns:
            The DataFrame with NaN rows removed.
        """
        if self.rawdata_df is None:
            raise RuntimeError("Data must be parsed before calling NaT_removal.")

        self.rawdata_df.dropna(inplace=True)
        return self.rawdata_df
