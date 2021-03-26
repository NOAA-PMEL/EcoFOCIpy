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
        pass

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

    def institution_meta_data(self):
        """Add EcoFOCI base metadata"""
        pass

    def temporal_geospatioal_meta_data(self):
        """Add min/max lat/lon/time bounds"""
        attributes = {
            'Latitude-Deg_MM.dd_W':self.mooring_yaml['Deployment']['DeploymentLatitude'],
            'Longitude-Deg_MM.dd_N':self.mooring_yaml['Deployment']['DeploymentLongitude']}
        self.xdf.attrs.update(attributes)

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

        return self.xdf.sel(date_time=slice(starttime,endtime))


    def filename_const(self):

        #EcoFOCI standard mooring naming
        #18bsm2a_wpak.nc - {mooringid}_{instshortname}_{depth}m.nc
        try:
            mooringID_simple = "".join(self.mooring_yaml['MooringID'].split('-')).lower()
        except:
            mooringID_simple = 'xxxxxx'
        
        try:
            depth = str(int(self.mooring_yaml['Instrumentation'][self.instrument_id]['ActualDepth'])).zfill(4)
        except:
            depth = '0000'

        return( mooringID_simple+'_'+self.inst_shortname+'_'+depth+'m.nc' )

    def xarray2netcdf_save(self, xdf=None, filename='temp.nc'):
                
        xdf.to_netcdf(filename)
