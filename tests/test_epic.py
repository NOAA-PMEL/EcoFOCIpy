import datetime

import pytest
from EcoFOCIpy.epic import EPIC_timeconvert as EPIC

class TestClassEPICTime:
    def test_1d(self):
        testdate = EPIC.EPIC2Datetime([2440000,],[43200000+3600*1000,])
        assert testdate == [datetime.datetime(1968, 5, 23, 13, 0)]

    def test_2d(self):
        testdate = EPIC.EPIC2Datetime([2440000,2450000],[43200000,0])
        assert testdate == [datetime.datetime(1968, 5, 23, 12, 0), datetime.datetime(1995, 10, 9, 0, 0)]

    def test_1d_EPIC(self):
        testdate = EPIC.Datetime2EPIC(EPIC.EPIC2Datetime([2440000,],[43200000+3600*1000,]))
        assert testdate == ([2440000], [46800000])

    def test_2d_EPIC(self):
        testdate = EPIC.Datetime2EPIC(EPIC.EPIC2Datetime([2440000,2450000],[43200000,0]))
        assert testdate == ([2440000,2450000],[43200000,0])

