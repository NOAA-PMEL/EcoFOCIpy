"""Contains a collection of MTR equipment parsing.

These include:

* Version 3/4 (old version) [ ]
* Version 5 (MTRduino) [x]

"""
import datetime
import numpy as np
import pandas as pd


class mtrduino(object):
    r""" MicroTemperature Recorders (MTR) - 5k / MTRduino generation
    Collection of static methods to define MTR processing and conversion

    It is assumed the data passed here is preliminarily processed and has calibration
    functions already applied

    ToDO:  Allow raw data to be passed"""

    @staticmethod
    def parse(filename=None, datetime_index=True):
        r"""
        Basic Method to open and read mtrduino raw converted csv files
            
        """
        assert filename != None , 'Must provide a datafile'

        rawdata = pd.read_csv(
            filename, delimiter=",", parse_dates=["date_time"]
        )

        if datetime_index:
            rawdata_df = rawdata_df.set_index(pd.DatetimeIndex(rawdata_df['date_time'])).drop(['date_time'],axis=1)

        return rawdata_df

class mtr(object):
    r""" MicroTemperature Recorders (MTR)
    Collection of static methods to define MTR processing and conversion"""

    @staticmethod
    def parse(filename=None, return_header=True, datetime_index=True, version=4.0):
        r"""Parse MTR Data

            kwargs
            mtr_coef : list
            [CoefA, CoefB, CoefC]

        """
        assert filename != None , 'Must provide a datafile'

        skiprows = 0
        hexlines = {}
        header = []

        fobj = open(filename)

        for k, line in enumerate(fobj.readlines()):
            line = line.strip()
            if skiprows == 0:
                header = header + [line]

            if "READ" in line:  # Get end of header.
                skiprows = k

            if ("CMD" in line) and (k > skiprows) and (skiprows != 0) and (version != 4.1):  # Get end of file.
                break
            elif ("mtr>" in line) and (k > skiprows) and (skiprows != 0) and (version == 4.1):
                break

            if (k > skiprows) and (skiprows != 0):
                hexlines[k] = line

        if return_header:
            return(hexlines, header)
        else:
            return hexlines

        # ### create time and data streams
        # count = 0
        # time = {}
        # temp = {}
        # deltat = 0  # 10 min usually
        # for sam_num in data_dic:
        #     time[count] = declines[sam_num]["time"]
        #     try:
        #         deltat = (
        #             declines[count + 1]["time"] - declines[count]["time"]
        #         )  # in seconds
        #         deltat = deltat / 120  # number of samples per record and convert
        #     except:
        #         datetime.timedelta(0)
        #     # loop through dictionary rows
        #     for i_row in range(0, 10, 1):  # loop through rows
        #         for i_col in range(0, 12, 1):
        #             temp[count] = declines[sam_num]["resistance_" + str(i_row)][i_col]
        #             count += 1
        #             time[count] = time[count - 1] + deltat
        # time.pop(
        #     time.keys()[-1]
        # )  # delta function adds an extra step so remove last entry

    @staticmethod
    def hex2dec(data_dic, model_factor=4.0e08):
        """
        model factor parameter is based on serial number range 
        for counts to resistance conversion
        if (args.SerialNo / 1000 == 3) or (args.SerialNo / 1000 == 4):
            model_factor = 4.0e+08
        """
        sample_num = 0
        data = {}
        for k, v in data_dic.items():
            if len(v) == 16:  # timeword mmddyyhhmmssxxxx
                data[sample_num] = {
                    "time": datetime.datetime.strptime(v[:-4], "%m%d%y%H%M%S")
                }
                sample_num += 1
                start_data = 0
            elif len(v) == 4:  # checksum
                continue
            elif len(v) == 48:
                # resistance values - 4char hex, 12 measurements, 10 consecutive lines
                # break string into chunks with 4char
                count = 4
                row = [
                    "".join(x) for x in zip(*[list(v[z::count]) for z in range(count)])
                ]
                # convert to decimal
                row = [int(x, 16) for x in row]
                data[sample_num - 1]["resistance_" + str(start_data)] = [
                    (model_factor / x) if x != 0 else 0 for x in row
                ]
                start_data += 1
            else:
                pass
                # periodically, it is known that a measurement gets dropped and the line needs
                # to be filled to 48 characters

        return data

    def res2temp(self, data_dic, mtr_coef=[0,0,0]):
        """Wrapper around steinhart_hart equation to convert resistance into temperature

        Args:
            data_dic (_type_): MTR Data Dictionary
            mtr_coef (list, optional): _description_. Defaults to [0,0,0].

        Returns:
            _type_: _description_
        """
        
        for sam_num in data_dic:
            for k, v in data_dic[sam_num].items():
                if not k == "time":
                    data_dic[sam_num][k] = [
                        self.steinhart_hart(x, mtr_coef)
                        for x in data_dic[sam_num][k]
                    ]
        return data_dic

    def steinhart_hart(self, resistance, mtr_coef=[0,0,0]):
        """Convert resistance into temperature

        Args:
            resistance (_type_): _description_
            mtr_coef (list, optional): _description_. Defaults to [0,0,0].

        Returns:
            _type_: _description_
        """
        if resistance <= 0:
            shhh = 0
        else:
            shhh = (
                1.0
                / (
                    float(mtr_coef[0])
                    + (float(mtr_coef[1]) * np.log10(resistance))
                    + (float(mtr_coef[2]) * np.log10(resistance) ** 3)
                )
                - 273.15
            )

        return shhh

    def dic2df(self, data_dic):
        """_summary_

        Args:
            data_dic (_type_): MTR data dictionary
        """

        ### create time and data streams
        count = 0
        time = {}
        temp = {}
        deltat = 0  # 10 min usually
        for sam_num in data_dic:
            time[count] = data_dic[sam_num]["time"]
            try:
                deltat = (
                    data_dic[count + 1]["time"] - data_dic[count]["time"]
                )  # in seconds
                deltat = deltat / 120  # number of samples per record and convert
            except:
                datetime.timedelta(0)
            # loop through dictionary rows
            for i_row in range(0, 10, 1):  # loop through rows
                for i_col in range(0, 12, 1):
                    temp[count] = data_dic[sam_num]["resistance_" + str(i_row)][i_col]
                    count += 1
                    time[count] = time[count - 1] + deltat

        df = pd.DataFrame(temp.values(),list(time.values())[:-1]) #last time stamp is an error in routine
        df.index.rename('date_time',inplace=True)
        df.rename(columns = {0:'temperature'}, inplace = True)

        return df