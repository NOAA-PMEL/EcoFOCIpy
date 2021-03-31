"""Contains a collection of tools to save to netcdf.

These include:

* converting to xarray
* adding global attributes
* adding variable attributes

"""
import datetime

import xarray as xr


class EcoFOCI_CFnc_moored(object):
    """Designed for moored instrumentation.

    CTD data will use the seabird cnv package

    Other platforms:
        prawler
        glider
        saildrone

    will use their own class
    """

    def __init__(self, df=None, instrument_yaml='', mooring_yaml=None, instrument_id='', inst_shortname=''):
        """data is a pandas dataframe
        Wich is immediatly converted to xarray
        """
        
        self.xdf = df.to_xarray()
        self.instrument_yaml = instrument_yaml
        self.mooring_yaml = mooring_yaml
        self.instrument_id = instrument_id
        self.inst_shortname = inst_shortname

    def institution_meta_add(self, institution_yaml=''):
        """Add EcoFOCI base metadata"""
        attributes = {}

        self.xdf.attrs.update(attributes)

    def deployment_meta_add(self):
        """TODO: Validate content of times"""

        attributes = {
            'MooringID':self.mooring_yaml['MooringID'],
            'platform_deployment_date':self.mooring_yaml['Deployment']['DeploymentDateTimeGMT'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'platform_deployment_cruise_name': self.mooring_yaml['Deployment']['DeploymentCruise'],
            'platform_recovery_date':self.mooring_yaml['Recovery']['RecoveryDateTimeGMT'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'platform_recovery_cruise_name': self.mooring_yaml['Recovery']['RecoveryCruise'],
            'platform_deployment_recovery_comments': self.mooring_yaml['Notes'],
            'WaterDepth':self.mooring_yaml['Deployment']['DeploymentDepth']}

        self.xdf.attrs.update(attributes)

    def instrument_meta_data(self):
        """Add Instrument deployment specific global meta data:
        Serial No:
        Calibration Information:
        Associated Instruments (for platforms like SBE16/RCM)
        """
        attributes = {
            'InstrumentSerialNumber':self.mooring_yaml['Instrumentation'][self.instrument_id]}

        self.xdf.attrs.update(attributes)

    def expand_dimensions(self,dim_names=['latitude','longitude','depth'],geophys_sort=True):
        """provide other dimensions in our usual x,y,z,t framework
        For moorings, this adds lat,lon,depth

        also rename the time dimension from `date_time` to `time`
        """
        self.xdf = self.xdf.expand_dims(dim_names).rename({'date_time':'time'})

        if geophys_sort:
            self.xdf = self.xdf.transpose('time','depth','latitude','longitude')
            self.xdf = self.xdf.assign_coords({"longitude": ("longitude", [1e35])})
            self.xdf = self.xdf.assign_coords({"latitude": ("latitude", [1e35])})
            self.xdf = self.xdf.assign_coords({"depth": ("depth", [1e35])})

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

    def temporal_geospatioal_meta_data(self,positiveE=True,depth=['designed']):
        """Add min/max lat/lon/time bounds"""
        attributes = {
            'Latitude-Deg_MM.dd_W':self.mooring_yaml['Deployment']['DeploymentLatitude'],
            'Longitude-Deg_MM.dd_N':self.mooring_yaml['Deployment']['DeploymentLongitude']}
        self.xdf.attrs.update(attributes)

        dd,mm,hh = self.mooring_yaml['Deployment']['DeploymentLongitude'].split()
        longitude = float(dd)+float(mm)/60
        ddlon,mmlon,hhlon = self.mooring_yaml['Deployment']['DeploymentLatitude'].split()
        latitude = float(ddlon)+float(mmlon)/60

        if 'w' in hh.lower():
            self.xdf['longitude'] = [-1*longitude]
            self.xdf['latitude'] = [latitude]
        else:
            self.xdf['longitude'] = [longitude]
            self.xdf['latitude'] = [latitude]

        if depth.lower() in ['designed']:
            self.xdf['depth'] = [self.mooring_yaml['Instrumentation'][self.instrument_id]['DesignedDepth']]
        elif depth.lower() in ['actual']:
            self.xdf['depth'] = [self.mooring_yaml['Instrumentation'][self.instrument_id]['ActualDepth']]
        else:
            self.xdf['depth'] = 1e35

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

    ###
    def autotrim_time(self):
        """using the recorded deployment/recovery records - trim time array
        """
        starttime = self.mooring_yaml['Deployment']['DeploymentDateTimeGMT']
        endtime = self.mooring_yaml['Recovery']['RecoveryDateTimeGMT']
        
        try:   
            self.history(history_text=self.xdf.attrs['history'] + '\nTrimmed to deployment.')
        except:   
            self.history(history_text='Trimmed to deployment.')

        return self.xdf.sel(time=slice(starttime,endtime))

    def get_xdf(self):
        """
        """

        return self.xdf


    def filename_const(self, depth='designed', manual_label=''):

        #EcoFOCI standard mooring naming
        #18bsm2a_wpak.nc - {mooringid}_{instshortname}_{depth}m.nc
        try:
            mooringID_simple = "".join(self.mooring_yaml['MooringID'].split('-')).lower()
        except:
            mooringID_simple = 'xxxxxx'

        if depth.lower() in ['designed']:
            depth = str(int(self.mooring_yaml['Instrumentation'][self.instrument_id]['DesignedDepth'])).zfill(4)
        elif depth.lower() in ['actual']:
            depth = str(int(self.mooring_yaml['Instrumentation'][self.instrument_id]['ActualDepth'])).zfill(4)
        else:
            depth = '0000'

        if not manual_label:
            return( mooringID_simple+'_'+self.inst_shortname+'_'+depth+'m.nc' )
        else:
            return( manual_label+'.nc' )

    def xarray2netcdf_save(self, xdf=None, filename='temp.nc', **kwargs):
                
        xdf.to_netcdf(filename,format=kwargs['format'])
