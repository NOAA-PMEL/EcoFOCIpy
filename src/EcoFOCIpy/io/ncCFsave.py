"""Contains a collection of tools to save to netcdf.

These include:

* converting to xarray
* adding global attributes
* adding variable attributes

"""
import xarray as xr
 

class EcoFOCI_CFnc(object):

    def __init__(self, df=None, instrument_meta=None, mooring_meta=None, instrument_id='', inst_shortname=''):
        """data is a pandas dataframe
        Wich is immediatly converted to xarray
        """
        
        self.xdf = df.to_xarray()
        self.instrument_meta = instrument_meta
        self.mooring_meta = mooring_meta
        self.instrument_id = instrument_id
        self.inst_shortname = inst_shortname

    def inst_meta_add(self):
        pass

    def deployment_meta_add(self):
        
        attributes = {'MooringID':self.mooring_meta['MooringID'],
                    'Deployment_Cruise': self.mooring_meta['Deployment']['DeploymentCruise'],
                    'Recovery_Cruise': self.mooring_meta['Recovery']['RecoveryCruise'],
                    'WaterDepth':self.mooring_meta['Deployment']['DeploymentDepth'],
                    'Latitude-Deg_MM.dd_W':self.mooring_meta['Deployment']['DeploymentLatitude'],
                    'Longitude-Deg_MM.dd_N':self.mooring_meta['Deployment']['DeploymentLongitude']}

        self.xdf.attrs = attributes

    def institution_meta_data(self):
        pass

    def autotrim_time(self):
        """using the recorded deployment/recovery records - trim array
        """
        starttime = self.mooring_meta['Deployment']['DeploymentDateTimeGMT']
        endtime = self.mooring_meta['Recovery']['RecoveryDateTimeGMT']
        
        return self.xdf.sel(date_time=slice(starttime,endtime))

    def filename_const(self):

        #EcoFOCI standard mooring naming
        #18bsm2a_wpak.nc - {mooringid}_{instshortname}_{depth}m.nc
        try:
            mooringID_simple = "".join(self.mooring_meta['MooringID'].split('-')).lower()
        except:
            mooringID_simple = 'xxxxxx'
        
        try:
            depth = str(int(self.mooring_confg['Instrumentation'][self.instrument_id]['ActualDepth'])).zfill(4)
        except:
            depth = '0000'

        return( mooringID_simple+'_'+self.inst_shortname+'_'+depth+'m.nc' )

    def xarray2netcdf_save(self, xdf=None, filename='temp.nc'):
                
        xdf.to_netcdf(filename)
