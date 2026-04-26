def cooling_load_from_area(area_m2, load_w_m2):
    kw = area_m2 * load_w_m2 / 1000
    tr = kw / 3.517
    return kw, tr


def fresh_air_cfm(occupancy, cfm_per_person):
    return occupancy * cfm_per_person


def ahu_cfm(cooling_tr, cfm_per_tr=400):
    return cooling_tr * cfm_per_tr


def transformer_dg_sizing(connected_kw, demand_factor, pf):
    demand_kw = connected_kw * demand_factor
    transformer_kva = demand_kw / pf if pf > 0 else 0
    recommended_transformer_kva = transformer_kva * 1.25
    dg_kva = transformer_kva * 1.10
    return demand_kw, recommended_transformer_kva, dg_kva


def water_tank_sizing(occupancy, lpd, ug_days=1.5, oh_percent=30):
    daily_liters = occupancy * lpd
    ug_tank_liters = daily_liters * ug_days
    oh_tank_liters = daily_liters * oh_percent / 100
    return daily_liters, ug_tank_liters, oh_tank_liters


def pump_sizing(flow_lpm, head_m, efficiency=0.65):
    q_m3s = flow_lpm / 60000
    kw = (1000 * 9.81 * q_m3s * head_m) / (1000 * efficiency)
    hp = kw / 0.746
    return kw, hp


def solar_roof_battery(annual_kwh, solar_gen_factor, panel_wp, roof_area_m2, backup_hours, critical_load_kw):
    required_kwp = annual_kwh / solar_gen_factor if solar_gen_factor > 0 else 0
    panel_count = (required_kwp * 1000) / panel_wp if panel_wp > 0 else 0
    roof_area_required = required_kwp * 10
    roof_capacity_kwp = roof_area_m2 / 10
    battery_kwh = critical_load_kw * backup_hours
    inverter_kw = required_kwp * 0.8
    return required_kwp, panel_count, roof_area_required, roof_capacity_kwp, battery_kwh, inverter_kw