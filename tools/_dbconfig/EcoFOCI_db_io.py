#!/usr/bin/env python

"""
 Background:
 --------
 EcoFOCI_db_io.py
 
 
 Purpose:
 --------
 Various Routines and Classes to interface with the mysql database that houses EcoFOCI meta data
 
  History:
 --------
 2017-07-28 S.Bell - replace pymsyql with mysql.connector -> provides purepython connection and prepared statements

"""

import mysql.connector
import datetime
import numpy as np

from EcoFOCIpy.metaconfig import load_config

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2017, 7, 28)
__modified__ = datetime.datetime(2021, 3, 25)


class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _float64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _int32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)

    def _int64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)


class EcoFOCI_db_datastatus(object):
    """Class definitions to access EcoFOCI Mooring Database"""
    
    def connect_to_DB(self, db_config_file=None,ftype=None):
        """Try to establish database connection

        Parameters
        ----------
        db_config_file : str
            full path to json formatted database config file    

        """
        self.db_config = load_config.load_config(db_config_file)
        try:
            self.db = mysql.connector.connect(host=self.db_config['systems']['akutan']['host'], 
                                        user=self.db_config['login']['user'],
                                        password=self.db_config['login']['password'], 
                                        database=self.db_config['database']['database'], 
                                        port=self.db_config['systems']['akutan']['port'])
        except:
            print("db error")
            
        #self.db.set_converter_class(NumpyMySQLConverter)

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor(dictionary=True)
        return(self.db,self.cursor)

    def manual_connect_to_DB(
        self,
        host="localhost",
        user="viewer",
        password=None,
        database="ecofoci",
        port=3306,
    ):
        """Try to establish database connection

		Parameters
		----------
		host : str
			ip or domain name of host
		user : str
			account user
		password : str
			account password
		database : str
			database name to connect to
		port : int
			database port

		"""
        db_config = {}
        db_config["host"] = host
        db_config["user"] = user
        db_config["password"] = password
        db_config["database"] = database
        db_config["port"] = port

        try:
            self.db = mysql.connector.connect(**db_config)
        except:
            print("db error")

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor(dictionary=True)
        self.prepcursor = self.db.cursor(prepared=True)
        return (self.db, self.cursor)

    def read_table(self, table=None, verbose=False, index_str="id", **kwargs):
        """build sql call based on kwargs"""

        if ("mooringid" in kwargs.keys()) and ("year" in kwargs.keys()):
            sql = ("SELECT * FROM `{0}` WHERE `mooringid`='{1}' and `year`={2}").format(
                table, kwargs["mooringid"], kwargs["year"]
            )
        elif "year" in kwargs.keys():
            sql = ("SELECT * FROM `{0}` WHERE `year`={1}").format(table, kwargs["year"])
        elif "mooringid" in kwargs.keys():
            sql = ("SELECT * FROM `{0}` WHERE `mooringid`='{1}'").format(
                table, kwargs["mooringid"]
            )
        else:
            sql = ("SELECT * FROM `{0}` ").format(table)

        if verbose:
            print(sql)

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row[index_str]] = {
                    keys: row[keys] for val, keys in enumerate(row.keys())
                }
            return result_dic
        except:
            print("Error: unable to fecth data")

    def read_mooring_summary(self, table=None, verbose=False, **kwargs):
        """ output is mooringID indexed """
        if "mooringid" in kwargs.keys():
            sql = ("SELECT * FROM `{0}` WHERE `MooringID`='{1}'").format(
                table, kwargs["mooringid"]
            )
        elif "deployed" in kwargs.keys():
            sql = ("SELECT * FROM `{0}` WHERE `DeploymentStatus`='DEPLOYED'").format(
                table
            )
        else:
            sql = ("SELECT * FROM `{0}` ").format(table)

        if verbose:
            print(sql)

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row["MooringID"]] = {
                    keys: row[keys] for val, keys in enumerate(row.keys())
                }
            return result_dic
        except:
            print("Error: unable to fecth data")

    def read_mooring_inst(
        self, table=None, verbose=False, mooringid=None, isdeployed="y"
    ):
        """specific to get deployed instruments"""
        sql = (
            "SELECT * from `{0}` WHERE `MooringID`='{1}' AND `Deployed` = '{2}' Order By `Depth`"
        ).format(table, mooringid, isdeployed)

        if verbose:
            print(sql)

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row["InstType"] + row["SerialNo"]] = {
                    keys: row[keys] for val, keys in enumerate(row.keys())
                }
            return result_dic
        except:
            print("Error: unable to fecth data")

    def read_cruise_summary(self, table=None, verbose=False, cruiseid=None):
        """specific to get cruise info"""
        sql = ("SELECT * from `{0}` WHERE `CruiseID`='{1}'").format(table, cruiseid)

        if verbose:
            print(sql)

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row["CruiseID"]] = {
                    keys: row[keys] for val, keys in enumerate(row.keys())
                }
            return result_dic
        except:
            print("Error: unable to fecth data")

    def read_castlog_summary(self, table=None, verbose=False, cruiseid=None):
        """specific to get cruise info"""
        sql = ("SELECT * from `{0}` WHERE `CruiseID`='{1}'").format(table, cruiseid)

        if verbose:
            print(sql)

        result_dic = {}
        try:
            self.cursor.execute(sql)
            for row in self.cursor:
                result_dic[row["CruiseID"]] = {
                    keys: row[keys] for val, keys in enumerate(row.keys())
                }
            return result_dic
        except:
            print("Error: unable to fecth data")


    def close(self):
        """close database"""
        #self.prepcursor.close()
        self.cursor.close()
        self.db.close()