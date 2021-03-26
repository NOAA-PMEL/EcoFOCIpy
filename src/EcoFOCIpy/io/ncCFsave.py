"""Contains a collection of tools to save to netcdf.

These include:

* converting to xarray
* adding global attributes
* adding variable attributes

"""
import xarray as xr
 

class EcoFOCI_CFnc(object):

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
        
        attributes = {'MooringID':self.mooring_yaml['MooringID'],
                    'Deployment_Cruise': self.mooring_yaml['Deployment']['DeploymentCruise'],
                    'Recovery_Cruise': self.mooring_yaml['Recovery']['RecoveryCruise'],
                    'WaterDepth':self.mooring_yaml['Deployment']['DeploymentDepth'],
                    'Latitude-Deg_MM.dd_W':self.mooring_yaml['Deployment']['DeploymentLatitude'],
                    'Longitude-Deg_MM.dd_N':self.mooring_yaml['Deployment']['DeploymentLongitude']}

        self.xdf.attrs = attributes

    def institution_meta_data(self,):
        pass

    def autotrim_time(self):
        """using the recorded deployment/recovery records - trim array
        """
        starttime = self.mooring_yaml['Deployment']['DeploymentDateTimeGMT']
        endtime = self.mooring_yaml['Recovery']['RecoveryDateTimeGMT']
        
        return self.xdf.sel(date_time=slice(starttime,endtime))

    def filename_const(self):

        #EcoFOCI standard mooring naming
        #18bsm2a_wpak.nc - {mooringid}_{instshortname}_{depth}m.nc
        try:
            mooringID_simple = "".join(self.mooring_yaml['MooringID'].split('-')).lower()
        except:
            mooringID_simple = 'xxxxxx'
        
        try:
            depth = str(int(self.mooring_confg['Instrumentation'][self.instrument_id]['ActualDepth'])).zfill(4)
        except:
            depth = '0000'

        return( mooringID_simple+'_'+self.inst_shortname+'_'+depth+'m.nc' )

    def xarray2netcdf_save(self, xdf=None, filename='temp.nc'):
                
        xdf.to_netcdf(filename)
