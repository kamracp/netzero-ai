def calculate_energy(area_m2, monthly_kwh, tariff):
    annual_kwh = monthly_kwh * 12
    annual_cost = annual_kwh * tariff
    epi = annual_kwh / area_m2 if area_m2 > 0 else 0
    co2_tons = annual_kwh * 0.82 / 1000
    return annual_kwh, annual_cost, epi, co2_tons


def calculate_solar(annual_kwh, solar_generation_per_kwp=1500):
    return annual_kwh / solar_generation_per_kwp if solar_generation_per_kwp > 0 else 0


def calculate_net_zero_gap(annual_kwh, solar_kwp, solar_generation_per_kwp=1500):
    solar_generation = solar_kwp * solar_generation_per_kwp
    gap = annual_kwh - solar_generation
    net_zero_percent = (solar_generation / annual_kwh) * 100 if annual_kwh > 0 else 0
    return solar_generation, gap, net_zero_percent


def calculate_net_zero_balance(annual_kwh, solar_kwp, saving_percent, solar_generation_per_kwp=1500):
    reduced_load = annual_kwh * (1 - saving_percent / 100)
    solar_generation = solar_kwp * solar_generation_per_kwp
    balance = solar_generation - reduced_load
    coverage_percent = (solar_generation / reduced_load) * 100 if reduced_load > 0 else 0
    return reduced_load, solar_generation, balance, coverage_percent


def calculate_battery_size(daily_kwh, backup_hours, critical_load_percent):
    critical_load_kw = daily_kwh / 24 * critical_load_percent / 100
    battery_kwh = critical_load_kw * backup_hours
    return critical_load_kw, battery_kwh


def calculate_water(occupancy, water_lpd):
    daily_water_liters = occupancy * water_lpd
    annual_water_kl = daily_water_liters * 365 / 1000
    return daily_water_liters, annual_water_kl


def calculate_passive_score(roof_insulation, wall_insulation, glazing, orientation, shading):
    score = 0

    if roof_insulation:
        score += 25
    if wall_insulation:
        score += 20
    if glazing in ["Double Glazing", "Low-E Glass"]:
        score += 20
    if orientation in ["Good", "Optimized"]:
        score += 20
    if shading:
        score += 15

    cooling_reduction = score * 0.25
    return score, cooling_reduction


def calculate_hvac(chiller_kw, cooling_tr):
    kw_per_tr = chiller_kw / cooling_tr if cooling_tr > 0 else 0

    if kw_per_tr <= 0.75:
        status = "Excellent"
    elif kw_per_tr <= 0.95:
        status = "Good"
    elif kw_per_tr <= 1.20:
        status = "Warning"
    else:
        status = "Poor"

    return kw_per_tr, status


def calculate_lighting(area_m2, lighting_kw):
    lighting_w_per_m2 = (lighting_kw * 1000) / area_m2 if area_m2 > 0 else 0

    if lighting_w_per_m2 <= 8:
        status = "Pass"
    elif lighting_w_per_m2 <= 12:
        status = "Warning"
    else:
        status = "High"

    return lighting_w_per_m2, status


def calculate_electrical(monthly_kwh, power_factor, load_factor):
    average_kw = monthly_kwh / (30 * 24) if monthly_kwh > 0 else 0
    estimated_max_kw = average_kw / load_factor if load_factor > 0 else 0
    estimated_kva = estimated_max_kw / power_factor if power_factor > 0 else 0
    recommended_transformer_kva = estimated_kva * 1.25
    return average_kw, estimated_max_kw, estimated_kva, recommended_transformer_kva


def calculate_roi(annual_cost, saving_percent, investment):
    annual_saving = annual_cost * saving_percent / 100
    payback_years = investment / annual_saving if annual_saving > 0 else 0
    return annual_saving, payback_years


def calculate_score(epi, net_zero_coverage, co2_ppm, passive_score):
    score = 100

    if epi > 250:
        score -= 25
    elif epi > 150:
        score -= 15
    elif epi > 100:
        score -= 8

    if net_zero_coverage < 50:
        score -= 20
    elif net_zero_coverage < 75:
        score -= 10

    if co2_ppm > 1200:
        score -= 20
    elif co2_ppm > 1000:
        score -= 10
    elif co2_ppm > 800:
        score -= 5

    if passive_score < 50:
        score -= 15

    return max(score, 0)