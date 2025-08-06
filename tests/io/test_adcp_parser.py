import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from EcoFOCIpy.io.adcp_parser import adcp

class DummyGeoMag:
    def GeoMag(self, lat, lon, time=None):
        class Result:
            dec = 10.0
        return Result()

class DummyGeoTools:
    @staticmethod
    def rotate_coord(u, v, decl):
        # Simple rotation for test
        return u + 1, v + 1

def test_load_rpt_file(tmp_path, monkeypatch):
    # Create a dummy .RPT file
    rpt_content = """
    Bin length = 2.0 m
    Distance to first bin = 5.0 m
    Number of bins = 10
    """
    rpt_file = tmp_path / "12345.RPT"
    rpt_file.write_text(rpt_content)
    parser = adcp(serial_no="12345", deployment_dir=tmp_path)
    lines, setup = parser.load_rpt_file()
    assert setup['bin_length'] == 2.0
    assert setup['distance_to_first_bin'] == 5.0
    assert setup['num_of_bins'] == 10
    assert len(lines) == 3

def test_bins2depth():
    parser = adcp(serial_no="12345")
    parser.setup = {'distance_to_first_bin': 5.0, 'num_of_bins': 3, 'bin_length': 2.0}
    result = parser.bins2depth(inst_depth=100)
    expected = np.arange(95.0, 89.0, -2.0)
    assert np.allclose(result, expected)

def test_mag_dec_corr(monkeypatch):
    parser = adcp(serial_no="12345")
    parser.vel_df = pd.DataFrame({'u_curr_comp': [1.0, 2.0], 'v_curr_comp': [3.0, 4.0]})
    monkeypatch.setattr('EcoFOCIpy.math.geomag.geomag.geomag', DummyGeoMag)
    monkeypatch.setattr('EcoFOCIpy.math.geotools', DummyGeoTools)
    # Patch ECOFOCIPY_AVAILABLE
    monkeypatch.setattr('EcoFOCIpy.io.adcp_parser.ECOFOCIPY_AVAILABLE', True)
    decl = parser.mag_dec_corr(60, 150, pd.Timestamp('2020-01-01'))
    assert decl == 10.0
    assert all(parser.vel_df['u_curr_comp'] == [2.0, 3.0])
    assert all(parser.vel_df['v_curr_comp'] == [4.0, 5.0])

def test_mag_dec_corr_importerror(monkeypatch):
    parser = adcp(serial_no="12345")
    parser.vel_df = pd.DataFrame({'u_curr_comp': [1.0], 'v_curr_comp': [2.0]})
    monkeypatch.setattr('EcoFOCIpy.io.adcp_parser.ECOFOCIPY_AVAILABLE', False)
    with pytest.raises(ImportError):
        parser.mag_dec_corr(60, 150, pd.Timestamp('2020-01-01'))

def test_mag_dec_corr_valuerror(monkeypatch):
    parser = adcp(serial_no="12345")
    parser.vel_df = None
    monkeypatch.setattr('EcoFOCIpy.io.adcp_parser.ECOFOCIPY_AVAILABLE', True)
    with pytest.raises(ValueError):
        parser.mag_dec_corr(60, 150, pd.Timestamp('2020-01-01'))
