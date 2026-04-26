def sensible_cooling_load_kw(area_m2, sensible_w_m2):
    return area_m2 * sensible_w_m2 / 1000


def total_cooling_load_tr(sensible_kw, fresh_air_kw, safety_factor=1.10):
    total_kw = (sensible_kw + fresh_air_kw) * safety_factor
    tr = total_kw / 3.517
    return total_kw, tr


def duct_area_from_cfm(cfm, velocity_fpm):
    area_ft2 = cfm / velocity_fpm if velocity_fpm > 0 else 0
    return area_ft2


def round_duct_diameter_mm(cfm, velocity_fpm):
    area_ft2 = duct_area_from_cfm(cfm, velocity_fpm)
    area_m2 = area_ft2 * 0.092903
    diameter_m = ((4 * area_m2 / 3.1416) ** 0.5) if area_m2 > 0 else 0
    return diameter_m * 1000


def chilled_water_flow_gpm(cooling_tr, delta_t_f=10):
    return cooling_tr * 24 / delta_t_f if delta_t_f > 0 else 0


def pump_power_kw(flow_m3hr, head_m, efficiency=0.70):
    q_m3s = flow_m3hr / 3600
    kw = (1000 * 9.81 * q_m3s * head_m) / (1000 * efficiency)
    return kw


def cooling_tower_tr(chiller_tr, heat_rejection_factor=1.25):
    return chiller_tr * heat_rejection_factor


def sensible_heat_ratio(sensible_kw, latent_kw):
    total = sensible_kw + latent_kw
    return sensible_kw / total if total > 0 else 0


def air_changes_per_hour(cfm, area_m2, height_m):
    volume_m3 = area_m2 * height_m
    airflow_m3hr = cfm * 1.699
    return airflow_m3hr / volume_m3 if volume_m3 > 0 else 0


def bypass_factor(t_entering, t_leaving, t_adp):
    denominator = t_entering - t_adp
    return (t_leaving - t_adp) / denominator if denominator != 0 else 0


def cfm_formula_based(total_hvac_kw, delta_t_c):
    delta_t_f = delta_t_c * 1.8
    btu_hr = total_hvac_kw * 3412
    return btu_hr / (1.08 * delta_t_f) if delta_t_f > 0 else 0


def hvac_saving_potential(total_hvac_tr, existing_chiller_kw, optimized_kw_per_tr, tariff, hours_per_day, days_per_year):
    ideal_kw = total_hvac_tr * optimized_kw_per_tr
    saving_kw = existing_chiller_kw - ideal_kw
    saving_kw = max(saving_kw, 0)
    saving_kwh = saving_kw * hours_per_day * days_per_year
    saving_cost = saving_kwh * tariff
    return ideal_kw, saving_kw, saving_kwh, saving_cost


def hvac_audit_score(kw_per_tr, shr, ach, bypass_factor_value):
    score = 100

    if kw_per_tr > 1.0:
        score -= 20
    if shr < 0.70:
        score -= 15
    if ach < 4:
        score -= 15
    if bypass_factor_value > 0.20:
        score -= 15

    return max(score, 0)