def get_recommendations(
    epi,
    net_zero_coverage,
    co2_ppm,
    water_lpd,
    kw_per_tr,
    lighting_w_m2,
    pf,
    passive_score,
    net_zero_balance
):
    rec = []

    if passive_score < 60:
        rec.append("Passive design weak है. Roof insulation, wall insulation, glazing, shading और orientation improve करें.")

    if epi > 150:
        rec.append("Energy intensity high है. HVAC, lighting और demand optimization priority पर रखें.")

    if kw_per_tr > 1.0:
        rec.append("HVAC efficiency weak है. Chiller performance, condenser cleaning, chilled water ΔT और VFD control check करें.")

    if lighting_w_m2 > 10:
        rec.append("Lighting load high है. LED retrofit, daylight control और occupancy sensors consider करें.")

    if pf < 0.95:
        rec.append("Power factor low है. APFC panel / capacitor bank check करें.")

    if net_zero_coverage < 100:
        rec.append("Renewable coverage insufficient है. Solar capacity, battery storage और net-metering feasibility revise करें.")

    if net_zero_balance < 0:
        rec.append("Net Zero gap exists. First reduce demand, then balance residual load with solar / renewable energy.")

    if co2_ppm > 1000:
        rec.append("CO₂ high है. Fresh air ventilation, occupancy control और IAQ monitoring improve करें.")

    if water_lpd > 135:
        rec.append("Water use high है. Leakage audit, low-flow fixtures, STP reuse और rainwater harvesting add करें.")

    if not rec:
        rec.append("Building performance acceptable है. Continuous monitoring और digital twin optimization शुरू करें.")

    return rec