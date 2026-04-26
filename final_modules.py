# ================= FIRE FIGHTING DESIGN =================

def fire_tank_sizing(hydrant_flow_lpm, sprinkler_flow_lpm, duration_min):
    total_flow_lpm = hydrant_flow_lpm + sprinkler_flow_lpm
    tank_liters = total_flow_lpm * duration_min
    tank_kl = tank_liters / 1000
    return total_flow_lpm, tank_liters, tank_kl


def fire_pump_sizing(flow_lpm, head_m, efficiency=0.70):
    q_m3s = flow_lpm / 60000
    kw = (1000 * 9.81 * q_m3s * head_m) / (1000 * efficiency)
    hp = kw / 0.746
    return kw, hp


def jockey_pump_sizing(fire_pump_flow_lpm):
    return fire_pump_flow_lpm * 0.03


# ================= PLUMBING / WATER DESIGN =================

def stp_sizing(occupancy, water_lpd, sewage_factor=0.8):
    sewage_lpd = occupancy * water_lpd * sewage_factor
    sewage_kld = sewage_lpd / 1000
    return sewage_lpd, sewage_kld


def rainwater_harvesting(roof_area_m2, rainfall_mm, runoff_coeff=0.8):
    water_liters = roof_area_m2 * rainfall_mm * runoff_coeff
    water_kl = water_liters / 1000
    return water_liters, water_kl


def hot_water_demand(occupancy, hot_water_lpd):
    daily_hot_water_liters = occupancy * hot_water_lpd
    return daily_hot_water_liters


# ================= WASTE / ESG / CARBON =================

def waste_generation(occupancy, waste_kg_person_day):
    daily_waste = occupancy * waste_kg_person_day
    annual_waste = daily_waste * 365
    return daily_waste, annual_waste


def organic_composter_size(daily_waste_kg, organic_percent):
    organic_waste = daily_waste_kg * organic_percent / 100
    return organic_waste


def biogas_potential(organic_waste_kg):
    biogas_m3_day = organic_waste_kg * 0.06
    return biogas_m3_day


def co2_avoided_from_solar(solar_generation_kwh, grid_factor=0.82):
    co2_kg = solar_generation_kwh * grid_factor
    co2_tons = co2_kg / 1000
    return co2_tons


def esg_score(net_zero_coverage, water_reuse_percent, waste_recycling_percent):
    score = 0

    score += min(net_zero_coverage, 100) * 0.4
    score += min(water_reuse_percent, 100) * 0.3
    score += min(waste_recycling_percent, 100) * 0.3

    return round(score, 1)