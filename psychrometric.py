import math


def saturation_pressure_kpa(temp_c):
    return 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))


def humidity_ratio(temp_c, rh_percent, pressure_kpa=101.325):
    pws = saturation_pressure_kpa(temp_c)
    pw = rh_percent / 100 * pws
    w = 0.62198 * pw / (pressure_kpa - pw)
    return w


def moist_air_enthalpy(temp_c, w):
    return 1.006 * temp_c + w * (2501 + 1.86 * temp_c)


def dew_point(temp_c, rh_percent):
    a = 17.27
    b = 237.3
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(rh_percent / 100)
    return (b * alpha) / (a - alpha)


def fresh_air_load_kw(outdoor_h, indoor_h, fresh_air_cfm):
    mass_flow_kg_s = fresh_air_cfm * 0.000566 * 1.2
    load_kw = mass_flow_kg_s * (outdoor_h - indoor_h)
    return max(load_kw, 0)


def kw_to_tr(kw):
    return kw / 3.517