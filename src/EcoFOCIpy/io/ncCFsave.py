"""Contains a collection of tools to save to netcdf.

These include:

* converting to xarray
* adding global attributes
* adding variable attributes

"""
import datetime

import xarray as xr



class EcoFOCI_CFnc_profile(object):
    """Designed for ctd profiles.

    Other platforms:
        prawler
        glider
        saildrone

    will use their own class
    """

    def __init__(self, df=None, instrument_yaml='', cruise_yaml=None, instrument_id=''):
        """data is a pandas dataframe
        Wich is immediatly converted to xarray
        """
        
        self.xdf = df.to_xarray()
        self.instrument_yaml = instrument_yaml
        self.cruise_yaml = cruise_yaml

    def institution_meta_add(self, institution_yaml=''):
        """Add EcoFOCI base metadata"""
        attributes = institution_yaml

        self.xdf.attrs.update(attributes)

    def deployment_meta_add(self,conscastno=''):
        """TODO: Validate content of times"""

        attributes = {
            'CruiseID':self.cruise_yaml['CTDCasts'][conscastno]['UniqueCruiseID'],
            'VesselName':self.cruise_yaml['CTDCasts'][conscastno]['Vessel'],
            'WaterDepth':self.cruise_yaml['CTDCasts'][conscastno]['BottomDepth']}

        self.xdf.attrs.update(attributes)

    def instrument_meta_data(self):
        """Add Instrument deployment specific global meta data:
        Serial No:
        Calibration Information:
        Associated Instruments (for platforms like SBE16/RCM)
        """
        attributes = {
            'InstrumentSerialNumber':None}

        self.xdf.attrs.update(attributes)

    def expand_dimensions(self,dim_names=['latitude','longitude','time'],geophys_sort=True):
        """provide other dimensions in our usual x,y,z,t framework
        For moorings, this adds lat,lon,time

        """
        self.xdf = self.xdf.expand_dims(dim_names).rename({'Pressure [dbar]':'depth'})

        if geophys_sort:
            self.xdf = self.xdf.transpose('time','depth','latitude','longitude')
            self.xdf = self.xdf.assign_coords({"longitude": ("longitude", [1e35])})
            self.xdf = self.xdf.assign_coords({"latitude": ("latitude", [1e35])})
            #self.xdf = self.xdf.assign_coords({"depth": ("depth", [1e35])})
            self.xdf = self.xdf.assign_coords({"time": ("time", [1e35])})

    def variable_meta_data(self,variable_keys=None,drop_missing=True):
        """Add CF meta_data to each known variable"""
        assert variable_keys != None , 'Must provide a list of variable names'

        for var in variable_keys:
            try:
                self.xdf[var].attrs = self.instrument_yaml[var]
            except:
                if drop_missing:
                    self.xdf = self.xdf.drop_vars(var)
                else:
                    pass

    def dimension_meta_data(self,variable_keys=None):
        """Add CF meta_data to each known dimension"""
        assert variable_keys != None , 'Must provide a list of variable names'

        for var in variable_keys:
            self.xdf[var].attrs = self.instrument_yaml[var]


    def provinance_meta_add(self):
        """add creation time and placeholder for modified time"""
        attributes = {
            'date_created':datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'date_modified': ''}
        self.xdf.attrs.update(attributes)

    ### Break out following methods for modification to existing data
    def history(self, history_text=''):
        """TODO: prevent overwriting?"""

        self.xdf.attrs.update({'history':history_text})

    def qc_status(self,qc_status='unknown'):
        """QC_indicator: Unknown, Excellent, ProbablyGood, Mixed"""
        attributes = {'QC_indicator':qc_status}
        self.xdf.attrs.update(attributes)


    def get_xdf(self):
        """
        """

        return self.xdf


    def filename_const(self, manual_label=''):

        #EcoFOCI standard ctd naming
        #DY1805c001_ctd.nc - {cruiseid}c{consecutivecastnumber}_ctd.nc

        if not manual_label:
            print('not implemented for profiles')
        else:
            return( manual_label+'.nc' )

    def xarray2netcdf_save(self, xdf=None, filename='temp.nc', **kwargs):
                
        xdf.to_netcdf(filename,format=kwargs['format'])
