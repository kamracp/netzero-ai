def wall_u_value(rsi_inside, wall_r_value, rsi_outside=0.04):
    total_r = rsi_inside + wall_r_value + rsi_outside
    return 1 / total_r if total_r > 0 else 0


def roof_u_value(rsi_inside, insulation_thickness_mm, insulation_k, roof_base_r, rsi_outside=0.04):
    insulation_r = (insulation_thickness_mm / 1000) / insulation_k if insulation_k > 0 else 0
    total_r = rsi_inside + roof_base_r + insulation_r + rsi_outside
    return insulation_r, (1 / total_r if total_r > 0 else 0)


def window_to_wall_ratio(window_area_m2, wall_area_m2):
    return (window_area_m2 / wall_area_m2) * 100 if wall_area_m2 > 0 else 0


def shading_depth(window_height_m, solar_altitude_deg):
    import math
    angle_rad = math.radians(solar_altitude_deg)
    return window_height_m / math.tan(angle_rad) if solar_altitude_deg > 0 else 0


def glass_status(shgc):
    if shgc <= 0.25:
        return "Excellent"
    elif shgc <= 0.35:
        return "Good"
    elif shgc <= 0.45:
        return "Warning"
    else:
        return "High Solar Gain"


def envelope_score(wall_u, roof_u, wwr, shgc):
    score = 100

    if wall_u > 0.8:
        score -= 20
    if roof_u > 0.6:
        score -= 25
    if wwr > 50:
        score -= 20
    if shgc > 0.45:
        score -= 20

    return max(score, 0)