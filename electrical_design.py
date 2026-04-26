import math


def full_load_current_kw(power_kw, voltage=415, pf=0.9):
    current = (power_kw * 1000) / (1.732 * voltage * pf)
    return current


def cable_size_selection(current):
    if current <= 20:
        return "4 sqmm"
    elif current <= 35:
        return "6 sqmm"
    elif current <= 50:
        return "10 sqmm"
    elif current <= 80:
        return "16 sqmm"
    elif current <= 120:
        return "25 sqmm"
    elif current <= 160:
        return "35 sqmm"
    elif current <= 200:
        return "50 sqmm"
    else:
        return "95 sqmm or parallel"


def breaker_size(current):
    return round(current * 1.25, 0)


def voltage_drop(current, length_m, cable_resistance=0.000018):
    vd = current * cable_resistance * length_m * 2
    return vd


def capacitor_kvar(load_kw, pf_initial, pf_target=0.98):
    phi1 = math.acos(pf_initial)
    phi2 = math.acos(pf_target)
    kvar = load_kw * (math.tan(phi1) - math.tan(phi2))
    return kvar


def dg_sizing_kva(load_kw, pf=0.8):
    return load_kw / pf


def panel_rating(current):
    return round(current * 1.25, 0)