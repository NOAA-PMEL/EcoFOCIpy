"""
WPAK Example
============

Demonstrate how to use the routines to process downloaded wpak data.

Not valid for argos data (NRT - only)
"""

from EcoFOCIpy import io.wpak_parser

testfile = '..staticdata/wpak_test.txt'
wpak = wpak_parser()

wpak.get_data(filename=testfile).parse()