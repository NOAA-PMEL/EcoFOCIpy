r"""
tests of the math functions
"""

import pytest
from ecofocipy.math import aandopt_oxy_corr as aand_oxy


class TestClassAandCorr:
    """
    Aanderaa Optode Corrections Tests
    """
    internal_salinity = 0
    actual_salinity = 34
    test_temperature = 2
    test_oxygen_conc_molar = 300
    def test_oxy_salcorr_zerosal(self):
        """
        Test that a salinity correction of 0PSU has no change
        """
        testsal = aand_oxy.o2_sal_comp(oxygen_conc=self.test_oxygen_conc_molar,
                                       salinity=self.internal_salinity,
                                       temperature=self.test_temperature,
                                       internal_sal=self.internal_salinity)
        assert testsal == self.test_oxygen_conc_molar
