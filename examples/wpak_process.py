"""
WPAK Example
============

Demonstrate how to use the routines to process downloaded wpak data.

Not valid for argos data (NRT - only)
"""

import src.EcoFOCIpy.io.wpak_parser as wpak_parser

testfile = '..staticdata/wpak_test.txt'

#init and load data
wpak = wpak_parser.wpak()
wpak_data = wpak.parse(filename=testfile,datetime_index=True) 

#time resample (or decimate)

"""
absolute simplest time gridding
 resample hourly will effectively truncate our times (only one data point in each hour)
 interpolate will fill some gaps
### like a time shift without adjusting data"""
wpak_grid_simple = wpak_data.resample('1H').mean().interpolate(limit=3)

"""
slightly more complex method - valid when data is far enough from the hour
 resample every 10min - but then linearly fill the supersampling
 then decimate to the hour
### very simple linear interpolation to hour"""
wpak_grid_decimate = wpak_data.resample('10T').mean().interpolate(limit=6)
wpak_grid_decimate = wpak_grid_decimate[wpak_grid_decimate.index.minute == 0]

# Ingest instrumenttype parameter config file for meta information
# Ingest mooring yaml status file for deployment meta information



# tests 
def sample_data_size_test(data=wpak_data):
    assert wpak_data.shape == (83, 13), 'test file not read in as expected - shape not right'
