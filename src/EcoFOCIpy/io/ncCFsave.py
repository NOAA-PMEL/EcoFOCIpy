"""Contains a collection of tools to save to netcdf.

These include:

* converting to xarray
* adding global attributes
* adding variable attributes
* adding metadata
* saving to netcdf

"""

import datetime

import numpy as np
import xarray as xr


class EcoFOCI_CFnc(object):
    """
    Designed for:
        - Cruise CTD's (cast, bottle, and discrete data)
        - moored instrumentation (1D and 2D)

    TODO:
    Following other platforms may use their own class:
        prawler
        glider
        saildrone
    """

    def __init__(
        self,
        df,
        instrument_yaml="",
        operation_yaml="",
        operation_type="mooring",
        instrument_id="",
        inst_shortname="",
    ):
        """[summary]

        Args:
            df (DataFrame): Pandas DataFrame of mesurement data.
            instrument_yaml (str, optional): yaml file with instrumentation meta attributes. Defaults to ''.
            operation_yaml (str, optional): yaml file with cruise or mooring meta attributes. Defaults to ''.
            operation_type (str, optional): Choose from 'mooring','ctd',''. Defaults to 'mooring'.
            instrument_id (str, optional): [description]. Defaults to ''.
            inst_shortname (str, optional): [description]. Defaults to ''.
        """
        assert operation_type in [
            "mooring",
            "ctd",
        ], "Operation type must be either 'mooring' or 'ctd'"

        self.xdf = df.to_xarray()
        self.instrument_yaml = instrument_yaml
        self.operation_yaml = operation_yaml
        self.operation_type = operation_type
        self.instrument_id = instrument_id
        self.inst_shortname = inst_shortname

    def institution_meta_add(self, institution_yaml=""):
        """Add EcoFOCI base metadata from ingested yaml file"""

        attributes = institution_yaml

        self.xdf.attrs.update(attributes)

    def deployment_meta_add(self, conscastno=""):
        """[summary]

        Args:
            conscastno (str, optional): only needed if operation type is 'ctd'. Defaults to ''.
        """

        if self.operation_type == "mooring":
            attributes = {
                "MooringID": self.operation_yaml["MooringID"],
                "platform_deployment_date": self.operation_yaml["Deployment"][
                    "DeploymentDateTimeGMT"
                ].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "platform_deployment_cruise_name": self.operation_yaml["Deployment"][
                    "DeploymentCruise"
                ],
                "platform_recovery_date": self.operation_yaml["Recovery"][
                    "RecoveryDateTimeGMT"
                ].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "platform_recovery_cruise_name": self.operation_yaml["Recovery"][
                    "RecoveryCruise"
                ],
                "platform_deployment_recovery_comments": self.operation_yaml["Notes"],
                "WaterDepth": self.operation_yaml["Deployment"]["DeploymentDepth"],
            }

        elif self.operation_type == "ctd":

            attributes = self.operation_yaml[
                list(self.operation_yaml.keys())[0]
            ]  # get first key which is always a cruise id

            # hacky way to clean up datetimes from yaml file that cause netcdf to balk
            try:
                attributes.pop("StartDate")
                attributes.pop("EndDate")
            except:
                pass

            attributes.update(
                {
                    "CruiseID": self.operation_yaml["CTDCasts"][conscastno][
                        "UniqueCruiseID"
                    ],
                    "VesselName": self.operation_yaml["CTDCasts"][conscastno]["Vessel"],
                    "WaterDepth": self.operation_yaml["CTDCasts"][conscastno][
                        "BottomDepth"
                    ],
                    "StationNameID": self.operation_yaml["CTDCasts"][conscastno][
                        "StationNameID"
                    ],
                    "Notes": self.operation_yaml["CTDCasts"][conscastno]["Notes"],
                    "InstrumentSerialNos": self.operation_yaml["CTDCasts"][conscastno][
                        "InstrumentSerialNos"
                    ],
                    "WindSpd": self.operation_yaml["CTDCasts"][conscastno]["WindSpd"],
                    "WindDir": self.operation_yaml["CTDCasts"][conscastno]["WindDir"],
                    "Pressure": self.operation_yaml["CTDCasts"][conscastno]["Pressure"],
                    "DryBulb": self.operation_yaml["CTDCasts"][conscastno]["DryBulb"],
                }
            )

        self.xdf.attrs.update(attributes)

    def instrument_meta_data(self):
        """Add Instrument deployment specific global meta data:
        Serial No:
        Calibration Information:
        Associated Instruments (for platforms like SBE16/RCM)
        """

        if self.operation_type == "mooring":
            attributes = {
                "InstrumentSerialNumber": self.operation_yaml["Instrumentation"][
                    self.instrument_id
                ]["SerialNo"],
                "InstrumentType": self.operation_yaml["Instrumentation"][
                    self.instrument_id
                ]["InstType"],
            }
        elif self.operation_type == "ctd":
            attributes = {"InstrumentSerialNumber": None}

        self.xdf.attrs.update(attributes)

    def expand_dimensions(
        self,
        dim_names=[
            "latitude",
            "longitude",
            "depth",
        ],
        time_dim_name="date_time",
        geophys_sort=True,
    ):
        """provide other dimensions in our usual x,y,z,t framework
        For moorings, this adds lat,lon,depth

        also rename the time dimension from `date_time` to `time`
        """
        self.xdf = self.xdf.expand_dims(dim_names)
        if self.operation_type == "mooring":
            self.xdf = self.xdf.rename({time_dim_name: "time"})

        # fill new dims
        for dn in dim_names:
            self.xdf = self.xdf.assign_coords({dn: (dn, [1e35])})

        if geophys_sort:
            self.xdf = self.xdf.transpose("time", "depth", "latitude", "longitude")

    def add_variable(self, variable_names=None, dupvar=None):
        """Add new empty variables"""
        assert variable_names != None, "Must provide a list of variable names"
        assert (
            dupvar != None
        ), "Must provide the name of a variable you want to use as a reference for the duplicate"

        for var in variable_names:
            try:
                self.xdf[variable_names] = self.xdf[dupvar] * np.nan
            except:
                pass

    def add_external_data(self, variable_names=None, data=None):
        """Add new empty variables"""
        assert variable_names != None, "Must provide a list of variable names"

        self.xdf[variable_names] = data

    def variable_meta_data(self, variable_keys=None, drop_missing=True):
        """Add CF meta_data to each known variable"""
        assert variable_keys != None, "Must provide a list of variable names"

        for var in variable_keys:
            try:
                self.xdf[var].attrs = self.instrument_yaml[var]
            except:
                if drop_missing:
                    self.xdf = self.xdf.drop_vars(var)
                else:
                    pass

    def dimension_meta_data(self, variable_keys=None):
        """Add CF meta_data to each known dimension"""
        assert variable_keys != None, "Must provide a list of variable names"

        for var in variable_keys:
            self.xdf[var].attrs = self.instrument_yaml[var]

    def temporal_geospatioal_meta_data_ctd(self, positiveE=True, conscastno="CTD001"):
        """Add cast lat, lon and time

        Args:
            positiveE (bool, optional): [description]. Defaults to True.
            conscastno (str, optional): [description]. Defaults to 'CTD001'.
        """
        assert self.operation_type == "ctd", "Function only relevant for ctds"

        GMTYear = self.operation_yaml["CTDCasts"][conscastno.upper()]["GMTYear"]
        GMTMonth = self.operation_yaml["CTDCasts"][conscastno.upper()][
            "GMTMonth"
        ]  # as 3char name
        GMTDay = self.operation_yaml["CTDCasts"][conscastno.upper()]["GMTDay"]
        GMTTime = self.operation_yaml["CTDCasts"][conscastno.upper()][
            "GMTTime"
        ]  # in seconds

        GMTDateTime = datetime.datetime.strptime(
            f"{GMTYear}-{GMTMonth}-{GMTDay}", "%Y-%b-%d"
        ) + datetime.timedelta(seconds=GMTTime)
        longitude = (
            float(self.operation_yaml["CTDCasts"][conscastno.upper()]["LongitudeDeg"])
            + (
                float(
                    self.operation_yaml["CTDCasts"][conscastno.upper()]["LongitudeMin"]
                )
            )
            / 60
        )
        latitude = (
            float(self.operation_yaml["CTDCasts"][conscastno.upper()]["LatitudeDeg"])
            + (
                float(
                    self.operation_yaml["CTDCasts"][conscastno.upper()]["LatitudeMin"]
                )
            )
            / 60
        )

        if not positiveE:
            self.xdf["longitude"] = [-1 * longitude]
        else:
            self.xdf["longitude"] = [longitude]
        self.xdf["latitude"] = [latitude]
        self.xdf["time"] = [GMTDateTime]

    def temporal_geospatioal_meta_data(self, positiveE=True, depth="designed"):
        """
        Moored Data only, CTD data has a similar function but castid must be passed

        Args:
            positiveE (bool, optional): [description]. Defaults to True.
            depth (list, optional): [description]. Defaults to 'designed'.
        """
        assert self.operation_type == "mooring", "Function only relevant for moorings"

        attributes = {
            "Latitude_DegMMddW": self.operation_yaml["Deployment"][
                "DeploymentLatitude"
            ],
            "Longitude_DegMMddN": self.operation_yaml["Deployment"][
                "DeploymentLongitude"
            ],
        }
        self.xdf.attrs.update(attributes)

        dd, mm, hh = self.operation_yaml["Deployment"]["DeploymentLongitude"].split()
        longitude = float(dd) + float(mm) / 60
        ddlon, mmlon = self.operation_yaml["Deployment"]["DeploymentLatitude"].split()[
            :2
        ]
        latitude = float(ddlon) + float(mmlon) / 60

        if "w" in hh.lower():
            self.xdf["longitude"] = [-1 * longitude]
            self.xdf["latitude"] = [latitude]
        else:
            self.xdf["longitude"] = [longitude]
            self.xdf["latitude"] = [latitude]

        if depth.lower() in ["designed"]:
            self.xdf["depth"] = [
                self.operation_yaml["Instrumentation"][self.instrument_id][
                    "DesignedDepth"
                ]
            ]
        elif depth.lower() in ["actual"]:
            self.xdf["depth"] = [
                self.operation_yaml["Instrumentation"][self.instrument_id][
                    "ActualDepth"
                ]
            ]
        elif depth.lower() in ["adcp"]:
            print("no change to depth variable")
        else:
            self.xdf["depth"] = 1e35

    def provinance_meta_add(self):
        """add creation time and placeholder for modified time"""
        attributes = {
            "date_created": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "date_modified": "",
        }
        self.xdf.attrs.update(attributes)

    def var_qcflag_init(self, dim_names=["depth", "latitude", "longitude", "time"]):
        """Skipping over dimensions (assumed profile if no dim_names passed), create qc_flag variables with autofil of 0

        Args:
            dim_names (list, optional): [list of variables that do not get qc_flags]. Defaults to ['depth','latitude','longitude','time'].

        """
        for i in self.xdf.variables:
            if (i not in dim_names) and ("_QC" not in i):
                self.xdf[i + "_QC"] = self.xdf[i] * 0
                self.xdf[i + "_QC"].attrs = {
                    "QCFlag_Value": "0,1,2,3,4,5,6,7,8,9",
                    "QCFlag_Meaning": """No QC performed,Good Data,Probably Good Data,
                 Bad Data that are Potentially Correctable, 
                 Bad Data, Value Changed,,Nominal Value, Interpolated Value, Missing Value""",
                }

    ### Break out following methods for modification to existing data
    def history(self, history_text=""):
        """TODO: prevent overwriting?"""

        self.xdf.attrs.update({"history": history_text})

    def qc_status(self, qc_status="unknown"):
        """Filewide QC_indicator: Unknown, Excellent, ProbablyGood, Mixed, UnQCd, QCd"""
        attributes = {"QC_indicator": qc_status}
        self.xdf.attrs.update(attributes)

    ###
    def interp2sfc(self, novars=["par"]):
        """Interpolate CTD files to suface, skip listed vars in novars, change QC_Flag to 8 or 9 if skipped

        Args:
            novars (list, optional): [Variables to not fill with values]. Defaults to ['par'].
        """
        assert self.operation_type == "ctd", "Function only relevant for ctds"

        tmpdata = self.xdf.isel({"depth": 0})
        while tmpdata.depth > 0:
            tmpdata["depth"] = tmpdata.depth - 1
            for varname in list(self.xdf.keys()):
                if "_QC" in varname:
                    tmpdata[varname] = 8
            for varname in novars:
                if varname in list(self.xdf.keys()):
                    tmpdata[varname] = np.nan
                    tmpdata[varname + "_QC"] = 9
            self.xdf = xr.concat([tmpdata, self.xdf], "depth")

    def autotrim_time(self):
        """Only used for moored data

        Returns:
            [type]: [description]
        """

        starttime = self.operation_yaml["Deployment"]["DeploymentDateTimeGMT"]
        endtime = self.operation_yaml["Recovery"]["RecoveryDateTimeGMT"]

        try:
            self.history(
                history_text=self.xdf.attrs["history"] + "\nTrimmed to deployment."
            )
        except:
            self.history(history_text="Trimmed to deployment.")

        return self.xdf.sel(time=slice(starttime, endtime))

    def get_xdf(self):
        """ """

        return self.xdf

    def xarray2netcdf_save(self, xdf, filename="temp.nc", **kwargs):
        """Save xarray to netcdf

        Args:
            xdf (xarray dataset): xarray dataset
            filename (str, optional): Filename. Defaults to 'temp.nc'.
        """

        xdf.to_netcdf(
            filename,
            format=kwargs["format"],
            encoding={"time": {"units": "days since 1900-01-01"}},
        )
