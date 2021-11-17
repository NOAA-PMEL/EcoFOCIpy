# EcoFOCI
"""Contains a collection of seabird equipment parsing
specifically tailored to sbe-ctd operations.

These include:

Profile SBE (cnv files):
* 9/11+
* FastCats

TODO: .btl, .ros
"""
import datetime
import sys

import ctd
import pandas as pd


def seabird_header(filename=None):
    r""" Seabird Instruments have a header usually defined by *END with a significant amount of
    information imbedded.  Send a flag to parse seabird headers.  Better yet may be to combine seabird gear
    into classes and subclasses.
    """
    assert filename.split('.')[-1] == 'cnv' , 'Must provide a tid file - use sbe software to convert'

    header, headercount, utc_time, latitude, longitude = [], [], [], [], []
    var_names = {}
    with open(filename) as fobj:
        for k, line in enumerate(fobj.readlines()):
            header = header + [line]
            if "# name" in line:
                var_names[int(line.split("=")[0].split()[-1])] = line.split("=")[1].split()[0].split(':')[0]
            if "* NMEA UTC (Time)" in line:
                utc_time = line.split("=")[-1].strip()
            if '* NMEA Latitude' in line:
                latitude = line.split("=")[-1].strip()
            if '* NMEA Longitude' in line:
                longitude = line.split("=")[-1].strip()                
            if "*END*" in line:
                headercount=k+1
                break

    return {'header':header, 'headercount':headercount, 'varnames':var_names, 'NMEAtime':utc_time, 'NMEALat':latitude, 'NMEALon':longitude}

class sbe_btl(object):
    """Process SBE BTL files

    Args:
        object ([type]): [description]

    Returns:
        [type]: [description]
    """
    @staticmethod
    def manual_parse(file_list=[None]):
        r"""
        Basic Method to open and read sbe9_11 .cnv files

        """
        assert file_list[0].split('.')[-1] == 'btl' , 'Must provide a btl file - use sbe software to convert'

        df_dic = {}

        for ctdfile in file_list:

            with open(ctdfile) as fobj:
                for k, line in enumerate(fobj.readlines()):
                    if (not "*" in line) & (not "#" in line):
                        if 'Bottle' in line:
                            line = line.replace('TurbWETntu0',' TurbWETntu0') #<- this is a common runon header
                            columns=line.lower().split() + ['time']
                            ctd_df= pd.DataFrame(columns=columns)
                        if 'avg' in line:
                            data=line.split('(avg)')[0].strip().split('   ')
                            try:
                                while True:
                                    data.remove('')
                            except ValueError:
                                pass
                        if 'sdev' in line:
                
                            row = pd.DataFrame(data=[data+[line.split()[0].strip()]],columns=columns)

                            for c in row.columns:
                                row[c] = row[c].astype(float,errors='ignore')

                            ctd_df =ctd_df.append(row)
            # index based on btl number and combine time/date
            ctd_df.set_index('bottle',inplace=True)
            ctd_df['datetime']=pd.to_datetime(ctd_df['date']+' '+ctd_df['time'])
            ctd_df = ctd_df.drop(['date','time'],axis=1)

            df_dic.update({ctdfile.split('/')[-1]:ctd_df})

        return df_dic

    @staticmethod
    def parse(file_list=[None]):
        """Use the CTD python package to read and process .btl files

        Args:
            file_list (list, optional): Full path to `.btl` files. Defaults to [None].

        Returns:
            [dictionary]: Dictionary of dataframes labeled by cruise cast number
        """
        assert file_list[0].split('.')[-1] == 'btl' , 'Must provide a btl file - use sbe software to convert'

        df_dic = {}
        for ctdfile in file_list:

            ctd_df = ctd.from_btl(ctdfile)

            df_dic.update({ctdfile.split('/')[-1]:ctd_df})

        return df_dic


class sbe9_11p(object):
    r""" Seabird 9/11+
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        There are quite a few instrument varations possible here - use the header meta to indentify variables

    """


    @staticmethod
    def parse(file_list=[None], datetime_index=True):
        r"""
        Basic Method to open and read sbe9_11 .cnv files

        """
        assert file_list[0].split('.')[-1] == 'cnv' , 'Must provide a cnv file - use sbe software to convert'

        df_dic = {}
        header_dic = {}
        for ctdfile in file_list:

            ctd_df = ctd.from_cnv(ctdfile)

            df_dic.update({ctdfile.split('/')[-1]:ctd_df})

            header_dic.update({ctdfile.split('/')[-1]:seabird_header(ctdfile)})

        return (df_dic, header_dic)

