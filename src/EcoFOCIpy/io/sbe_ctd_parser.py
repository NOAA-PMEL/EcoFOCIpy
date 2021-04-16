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

    header = []
    var_names = {}
    with open(filename) as fobj:
        for k, line in enumerate(fobj.readlines()):
            header = header + [line]
            if "# name" in line:
                var_names[int(line.split("=")[0].split()[-1])] = line.split("=")[1].split()[0].split(':')[0]
            if "# start_time" in line:
                start_time = line.split("[")[0].split("=")[-1].strip()
            if "*END*" in line:
                headercount=k+1
                break

    return (header, headercount, var_names, start_time)

class sbe_btl(object):
    @staticmethod
    def parse(file_list=[None]):
        r"""
        Basic Method to open and read sbe9_11 .cnv files

        """
        assert file_list[0].split('.')[-1] == 'btl' , 'Must provide a cnv file - use sbe software to convert'

        df_dic = {}

        for ctdfile in file_list:

            with open(ctdfile) as fobj:
                for k, line in enumerate(fobj.readlines()):
                    if not "#" in line:
                        headercount=k
                        columns = line.strip.split()
                        break
                
                ctd_df = pd.read_csv(ctdfile,skiprows=headercount+2,header=None,names=columns)

            df_dic.update({ctdfile.split('/')[-1]:ctd_df})

        return df_dic



class sbe9_11p(object):
    r""" Seabird 9/11+
        
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments

        There are quite a few instrument varations possible here - use the header meta to indentify variables

    """


    @staticmethod
    def parse(file_list=[None], return_header=True, datetime_index=True):
        r"""
        Basic Method to open and read sbe9_11 .cnv files

        """
        assert file_list[0].split('.')[-1] == 'cnv' , 'Must provide a cnv file - use sbe software to convert'

        df_dic = {}
        header_dic = {}
        for ctdfile in file_list:

            ctd_df = ctd.from_cnv(ctdfile)

            df_dic.update({ctdfile.split('/')[-1]:ctd_df})

        return (df_dic, header_dic)

