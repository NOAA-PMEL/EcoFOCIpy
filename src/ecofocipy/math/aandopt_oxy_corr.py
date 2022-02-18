"""
aandopt_oxy_corr.py

Apply Aanderaa Pressure and Salinity Corrections

Standard FOCI procedure has salinity set to 0PSU for deployment.
This is also the Aanderaa Factory setting.

"""

import numpy as np
import seawater as sw

def o2_sal_comp(oxygen_conc=None, salinity=None, temperature=None, internal_sal=0.0):
    """
    From Aandera April2007 -TD 218 Operating Manual - Oxygen Optodes (pg32)

    oxygen_conc - micromoles/kg
    salinity - salinity in ppt
    temperature
    B,C coefs

    """

    coefs = {
        "B0": -6.24097e-3,
        "B1": -6.93498e-3,
        "B2": -6.90358e-3,
        "B3": -4.29155e-3,
        "C0": -3.11680e-7,
    }

    scaled_temp = np.log((298.15 - temperature) / (273.15 + temperature))

    exp_a = salinity - internal_sal
    exp_b = (
        coefs["B0"]
        + coefs["B1"] * scaled_temp
        + coefs["B2"] * scaled_temp ** 2.0
        + coefs["B3"] * scaled_temp ** 3.0
    )
    exp_c = coefs["C0"] * (salinity ** 2.0 - internal_sal ** 2.0)

    return oxygen_conc * np.exp(exp_a * exp_b + exp_c)


def o2_dep_comp(oxygen_conc=None, depth=None):
    """
    From Aandera Operating Manual - Oxygen Optodes

    Small correction for normal FOCI operations (<500m) but should be used for deep stations
    """
    return oxygen_conc * (1.0 + (0.032 * depth) / 1000.0)


def o2_percent_sat(oxygen_conc=None, temperature=None, salinity=None, pressure=0):
    """
    calculate oxygen saturation
    Garcia and Gorden 1992 - from Seabird Derived Parameter Formulas
    """

    coefs = {
        "GG_A0": 2.00907,
        "GG_A1": 3.22014,
        "GG_A2": 4.0501,
        "GG_A3": 4.94457,
        "GG_A4": -0.256847,
        "GG_A5": 3.88767,
        "GG_B0": -0.00624523,
        "GG_B1": -0.00737614,
        "GG_B2": -0.010341,
        "GG_B3": -0.00817083,
        "GG_C0": -0.000000488682,
    }

    scaled_temp = np.log((298.15 - temperature) / (273.15 + temperature))

    oxsol_pri = np.exp(
        coefs["GG_A0"]
        + coefs["GG_A1"] * scaled_temp
        + coefs["GG_A2"] * (scaled_temp) ** 2
        + coefs["GG_A3"] * (scaled_temp) ** 3
        + coefs["GG_A4"] * (scaled_temp) ** 4
        + coefs["GG_A5"] * (scaled_temp) ** 5
        + salinity
        * (
            coefs["GG_B0"]
            + coefs["GG_B1"] * scaled_temp
            + coefs["GG_B2"] * (scaled_temp) ** 2
            + coefs["GG_B3"] * (scaled_temp) ** 3
        )
        + coefs["GG_C0"] * (salinity) ** 2
    )

    # determine sigmatheta and convert Oxygen from micromoles/kg to ml/l
    # calculate new oxygen saturation percent using derived oxsol
    sigmatheta_pri = sw.eos80.pden(salinity, temperature, pressure)
    oxy_percent_sat = ((oxygen_conc * sigmatheta_pri / 44660) / oxsol_pri) * 100.0

    return oxy_percent_sat


def o2_molar2umkg(oxygen_conc=None, salinity=None, temperature=None, pressure=None):
    """unit conversalinity=Noneion for micromole/liter -> micromole/kg"""

    sigmatheta_pri = sw.eos80.pden(salinity, temperature, pressure)
    density = sigmatheta_pri / 1000
    oxygen_conc = oxygen_conc / density

    return oxygen_conc
