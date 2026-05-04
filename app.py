import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from calculations import (
    calculate_energy,
    calculate_passive_score,
    calculate_solar,
    calculate_net_zero_balance,
    calculate_battery_size,
    calculate_water,
    calculate_hvac,
    calculate_lighting,
    calculate_electrical,
    calculate_roi,
    calculate_score
)

from recommendations import get_recommendations

from designer_sizing import (
    cooling_load_from_area,
    fresh_air_cfm,
    ahu_cfm,
    transformer_dg_sizing,
    water_tank_sizing,
    pump_sizing,
    solar_roof_battery
)

from psychrometric import (
    humidity_ratio,
    moist_air_enthalpy,
    dew_point,
    fresh_air_load_kw,
    kw_to_tr
)

from hvac_advanced import (
    sensible_cooling_load_kw,
    total_cooling_load_tr,
    duct_area_from_cfm,
    round_duct_diameter_mm,
    chilled_water_flow_gpm,
    pump_power_kw,
    cooling_tower_tr,
    sensible_heat_ratio,
    air_changes_per_hour,
    bypass_factor,
    cfm_formula_based,
    hvac_saving_potential,
    hvac_audit_score
)

from envelope_design import (
    wall_u_value,
    roof_u_value,
    window_u_value,
    window_to_wall_ratio,
    shading_depth,
    glass_status,
    envelope_score
)

from electrical_design import (
    full_load_current_kw,
    cable_size_selection,
    breaker_size,
    voltage_drop,
    capacitor_kvar,
    dg_sizing_kva,
    panel_rating
)

from final_modules import (
    fire_tank_sizing,
    fire_pump_sizing,
    jockey_pump_sizing,
    stp_sizing,
    rainwater_harvesting,
    hot_water_demand,
    waste_generation,
    organic_composter_size,
    biogas_potential,
    co2_avoided_from_solar,
    esg_score
)

from pdf_report import generate_pdf_report


st.set_page_config(
    page_title="Net Zero Building Digital Twin Platform",
    layout="wide"
)

st.title("Net Zero Building Digital Twin Platform")
st.caption("Energy | MEP Sizing | Weather | Psychrometric | HVAC | Electrical | Fire | Water | ESG | PDF Report")


# ================= SIDEBAR INPUTS =================

st.sidebar.header("Building Profile")

building_name = st.sidebar.text_input("Building Name", "Demo Commercial Building")
building_type = st.sidebar.selectbox(
    "Building Type",
    ["Office", "Hospital", "Hotel", "Mall", "Industrial Campus", "School"]
)

area_m2 = st.sidebar.number_input("Built-up Area (m²)", min_value=1.0, value=10000.0)
occupancy = st.sidebar.number_input("Occupancy (Persons)", min_value=1, value=500)

monthly_kwh = st.sidebar.number_input("Monthly Energy Consumption (kWh)", min_value=0.0, value=120000.0)
tariff = st.sidebar.number_input("Electricity Tariff (₹/kWh)", min_value=0.0, value=9.0)

st.sidebar.header("Passive Design Inputs")

roof_insulation = st.sidebar.checkbox("Roof Insulation Available", value=True)
wall_insulation = st.sidebar.checkbox("Wall Insulation Available", value=False)
glazing = st.sidebar.selectbox("Window Glazing Type", ["Single Glass", "Double Glazing", "Low-E Glass"])
orientation = st.sidebar.selectbox("Building Orientation Quality", ["Poor", "Average", "Good", "Optimized"])
shading = st.sidebar.checkbox("External Shading / Solar Control Available", value=True)

st.sidebar.header("Envelope Design Inputs")

wall_u_value = st.sidebar.number_input("Wall U-Value (W/m²K)", value=1.80)
inside_surface_r = st.sidebar.number_input("Inside Surface Resistance RSI", value=0.13)

roof_u_value = st.sidebar.number_input("Roof Base U-Value (W/m²K)", value=0.30)
roof_insulation_thickness = st.sidebar.number_input("Roof Insulation Thickness (mm)", value=50.0)
roof_insulation_k = st.sidebar.number_input("Roof Insulation Conductivity k (W/mK)", value=0.035)
roof_area_m2 = st.sidebar.number_input("Roof Area (m²)", value=1000.0)

wall_area_m2 = st.sidebar.number_input("External Wall Area (m²)", value=1000.0)
window_area_m2 = st.sidebar.number_input("Window Glass Area (m²)", value=300.0)

glass_shgc = st.sidebar.number_input("Glass SHGC", min_value=0.05, max_value=0.90, value=0.35)
window_u_value = st.sidebar.number_input("Window Base U-Value (W/m²K)", value=0.30)

window_height = st.sidebar.number_input("Window Height (m)", value=1.5)
solar_altitude = st.sidebar.number_input("Solar Altitude Angle (degree)", value=45.0)


st.sidebar.header("MEP Engineering Inputs")

chiller_kw = st.sidebar.number_input("Total Chiller / HVAC Power (kW)", min_value=0.0, value=650.0)
cooling_tr = st.sidebar.number_input("Actual Cooling Load (TR)", min_value=0.0, value=800.0)

lighting_kw = st.sidebar.number_input("Total Lighting Load (kW)", min_value=0.0, value=90.0)

power_factor = st.sidebar.number_input("Power Factor", min_value=0.1, max_value=1.0, value=0.92)
load_factor = st.sidebar.number_input("Load Factor", min_value=0.1, max_value=1.0, value=0.60)


st.sidebar.header("Electrical Detailed Inputs")

elec_load_kw = st.sidebar.number_input("Electrical Load (kW)", value=500.0)
cable_length = st.sidebar.number_input("Cable Length (m)", value=50.0)
pf_initial = st.sidebar.number_input("Existing Power Factor", value=0.85)
pf_target = st.sidebar.number_input("Target Power Factor", value=0.98)
system_voltage = st.sidebar.number_input("System Voltage (V)", value=415.0)


st.sidebar.header("Renewable & Net Zero Inputs")

solar_existing_kwp = st.sidebar.number_input("Existing / Proposed Solar Capacity (kWp)", min_value=0.0, value=300.0)
solar_generation_factor = st.sidebar.number_input("Solar Generation Factor (kWh/kWp/year)", min_value=500.0, value=1500.0)

saving_percent = st.sidebar.slider("Expected Energy Reduction (%)", 0, 60, 18)

backup_hours = st.sidebar.number_input("Battery Backup Hours", min_value=0.0, value=4.0)
critical_load_percent = st.sidebar.number_input("Critical Load (%)", min_value=0.0, max_value=100.0, value=30.0)

investment = st.sidebar.number_input("Estimated Investment (₹)", min_value=0.0, value=2500000.0)


st.sidebar.header("Water & IAQ Inputs")

water_lpd = st.sidebar.number_input("Water Consumption (Litres/Person/Day)", min_value=0.0, value=150.0)
co2_ppm = st.sidebar.number_input("Indoor CO₂ Level (ppm)", min_value=300.0, value=950.0)


st.sidebar.header("Designer Sizing Inputs")

# Translate Insulation Checkboxes to U-Values (W/m2.K)
# Uninsulated brick/concrete is typically ~2.5 U-value; Insulated is ~0.4
actual_wall_u_value = 0.4 if wall_insulation else 2.5 
actual_roof_u_value = 0.3 if roof_insulation else 2.0

# Translate Glazing Dropdown to U-Value and SHGC (Solar Heat Gain Coefficient)
if glazing == "Single Glass":
    actual_window_u = 5.8
    actual_shgc = 0.85  # Lets in 85% of solar heat
elif glazing == "Double Glazing":
    actual_window_u = 2.8
    actual_shgc = 0.70  # Lets in 70% of solar heat
elif glazing == "Low-E Glass":
    actual_window_u = 1.5
    actual_shgc = 0.40  # Blocks most solar heat, lets in light

# Translate Shading Checkbox to a Solar Modifier
# External shading physically blocks the sun from hitting the glass. 
# We'll assume a 50% reduction in direct solar heat if shading is active.
shading_multiplier = 0.5 if shading else 1.0

# Translate Orientation Quality to Peak Solar Irradiance (W/m2)
# "Poor" orientation means heavy East/West glass (high morning/afternoon sun).
# "Optimized" means heavy North/South glass (easy to shade, lower peak impact).
irradiance_map = {
    "Poor": 600,       # High peak solar load
    "Average": 500,
    "Good": 400,
    "Optimized": 300   # Lower peak solar load
}
peak_solar_irradiance = irradiance_map[orientation]

# Envelope Transmission (Sensible Conduction)
delta_T = max(0, outdoor_dbt - indoor_dbt) 
wall_load_w = actual_wall_u_value * wall_area_m2 * delta_T
roof_load_w = actual_roof_u_value * roof_area_m2 * delta_T
glass_cond_w = actual_window_u * window_area_m2 * delta_T

# Solar Gain (Sensible Radiation)
# Notice how SHGC, Shading Multiplier, and Orientation (Irradiance) all interact here!
glass_solar_w = window_area_m2 * actual_shgc * peak_solar_irradiance * shading_multiplier

# Internal Loads
internal_load_w = area_m2 * 25 # Standard commercial 25 W/m2

# Total Sensible Room Load
room_sensible_kw = (wall_load_w + roof_load_w + glass_cond_w + glass_solar_w + internal_load_w) / 1000

# Calculate Tons of Refrigeration
concept_cooling_tr = (room_sensible_kw + fresh_air_kw) / 3.516

cfm_per_person = st.sidebar.number_input("Fresh Air (CFM/person)", min_value=5.0, value=15.0)

connected_kw = st.sidebar.number_input("Connected Electrical Load (kW)", min_value=0.0, value=1000.0)
demand_factor = st.sidebar.number_input("Demand Factor", min_value=0.1, max_value=1.0, value=0.75)

ug_storage_days = st.sidebar.number_input("UG Tank Storage Days", min_value=0.5, value=1.5)
oh_tank_percent = st.sidebar.number_input("OH Tank % of Daily Demand", min_value=10.0, value=30.0)

pump_flow_lpm = st.sidebar.number_input("Pump Flow (LPM)", min_value=1.0, value=500.0)
pump_head_m = st.sidebar.number_input("Pump Head (m)", min_value=1.0, value=35.0)

roof_area_m2 = st.sidebar.number_input("Available Solar Roof Area (m²)", min_value=1.0, value=3000.0)
panel_wp = st.sidebar.number_input("Solar Panel Size (Wp)", min_value=100.0, value=550.0)


st.sidebar.header("Weather & Psychrometric Inputs")

outdoor_dbt = st.sidebar.number_input("Outdoor Dry Bulb Temperature DBT (°C)", value=38.0)
outdoor_rh = st.sidebar.number_input("Outdoor Relative Humidity RH (%)", min_value=1.0, max_value=100.0, value=55.0)

indoor_dbt = st.sidebar.number_input("Indoor Design Temperature DBT (°C)", value=24.0)
indoor_rh = st.sidebar.number_input("Indoor Relative Humidity RH (%)", min_value=1.0, max_value=100.0, value=50.0)

weather_fresh_air_cfm = st.sidebar.number_input("Fresh Air Quantity for Psychrometric Load (CFM)", min_value=0.0, value=5000.0)


st.sidebar.header("Advanced HVAC Sizing Inputs")

sensible_w_m2 = st.sidebar.number_input("Sensible Load Factor (W/m²)", value=90.0)
hvac_safety_factor = st.sidebar.number_input("HVAC Safety Factor", min_value=1.0, max_value=1.5, value=1.10)

duct_velocity_fpm = st.sidebar.number_input("Duct Velocity (FPM)", value=1500.0)

chw_delta_t_f = st.sidebar.number_input("Chilled Water ΔT (°F)", value=10.0)
chw_pump_head_m = st.sidebar.number_input("CHW Pump Head (m)", value=35.0)
pump_efficiency = st.sidebar.number_input("Pump Efficiency", min_value=0.1, max_value=1.0, value=0.70)
ceiling_height_m = st.sidebar.number_input("Ceiling Height (m)", value=3.5)
coil_adp_temp = st.sidebar.number_input("Coil ADP Temperature (°C)", value=12.0)

optimized_kw_per_tr = st.sidebar.number_input("Optimized HVAC Target (kW/TR)", value=0.75)
hvac_hours_per_day = st.sidebar.number_input("HVAC Operating Hours/day", value=18.0)
hvac_days_per_year = st.sidebar.number_input("HVAC Operating Days/year", value=300.0)

st.sidebar.header("Fire Fighting Inputs")

hydrant_flow_lpm = st.sidebar.number_input("Hydrant Flow (LPM)", value=2850.0)
sprinkler_flow_lpm = st.sidebar.number_input("Sprinkler Flow (LPM)", value=1000.0)
fire_duration_min = st.sidebar.number_input("Fire Storage Duration (min)", value=120.0)
fire_head_m = st.sidebar.number_input("Fire Pump Head (m)", value=70.0)


st.sidebar.header("Plumbing / STP / Rainwater Inputs")

rainfall_mm = st.sidebar.number_input("Design Rainfall (mm)", value=50.0)
hot_water_lpd = st.sidebar.number_input("Hot Water Demand (L/person/day)", value=20.0)
water_reuse_percent = st.sidebar.number_input("Water Reuse (%)", min_value=0.0, max_value=100.0, value=30.0)


st.sidebar.header("Waste / ESG Inputs")

waste_kg_person_day = st.sidebar.number_input("Waste Generation (kg/person/day)", value=0.6)
organic_percent = st.sidebar.number_input("Organic Waste (%)", min_value=0.0, max_value=100.0, value=50.0)
waste_recycling_percent = st.sidebar.number_input("Waste Recycling (%)", min_value=0.0, max_value=100.0, value=40.0)


# ================= CALCULATIONS =================

annual_kwh, annual_cost, epi, co2_tons = calculate_energy(area_m2, monthly_kwh, tariff)

passive_score, cooling_reduction_percent = calculate_passive_score(
    roof_insulation,
    wall_insulation,
    glazing,
    orientation,
    shading
)

wall_u = wall_u_value(inside_surface_r, wall_r_value)

roof_ins_r, roof_u = roof_u_value(
    inside_surface_r,
    roof_insulation_thickness,
    roof_insulation_k,
    roof_base_r
)

wwr_percent = window_to_wall_ratio(window_area, wall_area)
required_shading_depth = shading_depth(window_height, solar_altitude)
glass_performance = glass_status(glass_shgc)
env_score = envelope_score(wall_u, roof_u, wwr_percent, glass_shgc)

required_solar_kwp = calculate_solar(annual_kwh, solar_generation_factor)

reduced_load, solar_generation, net_zero_balance, net_zero_coverage = calculate_net_zero_balance(
    annual_kwh,
    solar_existing_kwp,
    saving_percent,
    solar_generation_factor
)

daily_kwh = reduced_load / 365 if reduced_load > 0 else 0
critical_load_kw, battery_kwh = calculate_battery_size(daily_kwh, backup_hours, critical_load_percent)

daily_water_liters, annual_water_kl = calculate_water(occupancy, water_lpd)

kw_per_tr, hvac_status = calculate_hvac(chiller_kw, cooling_tr)

lighting_w_m2, lighting_status = calculate_lighting(area_m2, lighting_kw)

average_kw, estimated_max_kw, estimated_kva, recommended_transformer_kva = calculate_electrical(
    monthly_kwh,
    power_factor,
    load_factor
)

annual_saving, payback_years = calculate_roi(annual_cost, saving_percent, investment)

score = calculate_score(epi, net_zero_coverage, co2_ppm, passive_score)

recommendations = get_recommendations(
    epi,
    net_zero_coverage,
    co2_ppm,
    water_lpd,
    kw_per_tr,
    lighting_w_m2,
    power_factor,
    passive_score,
    net_zero_balance
)


# Designer sizing calculations

# concept_cooling_kw, concept_cooling_tr = cooling_load_from_area(area_m2, load_w_m2)
total_fresh_air_cfm = fresh_air_cfm(occupancy, cfm_per_person)
total_ahu_cfm = ahu_cfm(concept_cooling_tr)

demand_kw, design_transformer_kva, design_dg_kva = transformer_dg_sizing(
    connected_kw,
    demand_factor,
    power_factor
)

daily_water_demand, ug_tank_liters, oh_tank_liters = water_tank_sizing(
    occupancy,
    water_lpd,
    ug_storage_days,
    oh_tank_percent
)

pump_kw, pump_hp = pump_sizing(pump_flow_lpm, pump_head_m)

required_kwp_design, panel_count, roof_area_required, roof_capacity_kwp, design_battery_kwh, inverter_kw = solar_roof_battery(
    annual_kwh,
    solar_generation_factor,
    panel_wp,
    roof_area_m2,
    backup_hours,
    critical_load_kw
)


# Psychrometric calculations

outdoor_w = humidity_ratio(outdoor_dbt, outdoor_rh)
indoor_w = humidity_ratio(indoor_dbt, indoor_rh)

outdoor_h = moist_air_enthalpy(outdoor_dbt, outdoor_w)
indoor_h = moist_air_enthalpy(indoor_dbt, indoor_w)

outdoor_dp = dew_point(outdoor_dbt, outdoor_rh)
indoor_dp = dew_point(indoor_dbt, indoor_rh)

fresh_air_kw = fresh_air_load_kw(outdoor_h, indoor_h, weather_fresh_air_cfm)
fresh_air_tr = kw_to_tr(fresh_air_kw)


# Advanced HVAC calculations

sensible_kw = sensible_cooling_load_kw(area_m2, sensible_w_m2)

total_hvac_kw, total_hvac_tr = total_cooling_load_tr(
    sensible_kw,
    fresh_air_kw,
    hvac_safety_factor
)

duct_area_ft2 = duct_area_from_cfm(total_ahu_cfm, duct_velocity_fpm)
round_duct_mm = round_duct_diameter_mm(total_ahu_cfm, duct_velocity_fpm)

chw_flow_gpm = chilled_water_flow_gpm(total_hvac_tr, chw_delta_t_f)
chw_flow_m3hr = chw_flow_gpm * 0.2271

chw_pump_kw = pump_power_kw(chw_flow_m3hr, chw_pump_head_m, pump_efficiency)

ct_tr = cooling_tower_tr(total_hvac_tr)
latent_kw = fresh_air_kw
shr_value = sensible_heat_ratio(sensible_kw, latent_kw)

ach_value = air_changes_per_hour(total_ahu_cfm, area_m2, ceiling_height_m)

bf_value = bypass_factor(outdoor_dbt, indoor_dbt, coil_adp_temp)

delta_t_c = outdoor_dbt - indoor_dbt
cfm_check = cfm_formula_based(total_hvac_kw, delta_t_c)

ideal_hvac_kw, saving_kw, saving_kwh_year, hvac_saving_cost = hvac_saving_potential(
    total_hvac_tr,
    chiller_kw,
    optimized_kw_per_tr,
    tariff,
    hvac_hours_per_day,
    hvac_days_per_year
)

hvac_score = hvac_audit_score(
    kw_per_tr,
    shr_value,
    ach_value,
    bf_value
)

# Electrical detailed calculations

elec_current = full_load_current_kw(elec_load_kw, system_voltage, pf_initial)
cable = cable_size_selection(elec_current)
breaker = breaker_size(elec_current)
vd = voltage_drop(elec_current, cable_length)
kvar = capacitor_kvar(elec_load_kw, pf_initial, pf_target)
dg = dg_sizing_kva(elec_load_kw)
panel = panel_rating(elec_current)


# Final module calculations

fire_total_flow, fire_tank_liters, fire_tank_kl = fire_tank_sizing(
    hydrant_flow_lpm,
    sprinkler_flow_lpm,
    fire_duration_min
)

fire_pump_kw, fire_pump_hp = fire_pump_sizing(
    fire_total_flow,
    fire_head_m
)

jockey_flow_lpm = jockey_pump_sizing(fire_total_flow)

sewage_lpd, stp_kld = stp_sizing(
    occupancy,
    water_lpd
)

rainwater_liters, rainwater_kl = rainwater_harvesting(
    roof_area_m2,
    rainfall_mm
)

hot_water_liters = hot_water_demand(
    occupancy,
    hot_water_lpd
)

daily_waste_kg, annual_waste_kg = waste_generation(
    occupancy,
    waste_kg_person_day
)

organic_waste_kg = organic_composter_size(
    daily_waste_kg,
    organic_percent
)

biogas_m3_day = biogas_potential(
    organic_waste_kg
)

solar_co2_avoided_tons = co2_avoided_from_solar(
    solar_generation
)

building_esg_score = esg_score(
    net_zero_coverage,
    water_reuse_percent,
    waste_recycling_percent
)


# ================= DASHBOARD =================

st.subheader(f"Project: {building_name}")
st.write(f"Building Type: **{building_type}**")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Annual Energy", f"{annual_kwh:,.0f} kWh")
col2.metric("Annual Energy Cost", f"₹ {annual_cost:,.0f}")
col3.metric("EPI", f"{epi:.1f} kWh/m²/year")
col4.metric("CO₂ Emission", f"{co2_tons:.1f} tons/year")

col5, col6, col7, col8 = st.columns(4)

col5.metric("Passive Design Score", f"{passive_score}/100")
col6.metric("Reduced Energy Load", f"{reduced_load:,.0f} kWh/year")
col7.metric("Net Zero Coverage", f"{net_zero_coverage:.1f}%")
col8.metric("Overall Score", f"{score}/100")


tab_overview, tab_envelope, tab_designer, tab_weather, tab_hvac_adv, tab_electrical, tab_final, tab_net_zero, tab_status, tab_report = st.tabs([
    "Building Overview",
    "Envelope Design",
    "Designer Sizing Tools",
    "Weather & Psychrometric",
    "Advanced HVAC",
    "Electrical Design",
    "Fire | Plumbing | ESG",
    "Net Zero & Renewable",
    "Performance Status",
    "Net Zero Report"
])


with tab_overview:

    st.subheader("Passive Design Performance")

    p1, p2 = st.columns(2)
    p1.metric("Passive Design Score", f"{passive_score}/100")
    p2.metric("Estimated Cooling Load Reduction", f"{cooling_reduction_percent:.1f}%")

    st.subheader("HVAC Performance")

    h1, h2 = st.columns(2)
    h1.metric("HVAC Efficiency", f"{kw_per_tr:.2f} kW/TR")
    h2.metric("HVAC Status", hvac_status)

    st.subheader("Electrical Performance")

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Average Load", f"{average_kw:.1f} kW")
    e2.metric("Estimated Max Load", f"{estimated_max_kw:.1f} kW")
    e3.metric("Estimated Demand", f"{estimated_kva:.1f} kVA")
    e4.metric("Recommended Transformer", f"{recommended_transformer_kva:.1f} kVA")

    st.subheader("Lighting Performance")

    l1, l2 = st.columns(2)
    l1.metric("Lighting Power Density", f"{lighting_w_m2:.1f} W/m²")
    l2.metric("Lighting Status", lighting_status)


with tab_envelope:

    st.subheader("Building Envelope Design")

    ev1, ev2, ev3, ev4 = st.columns(4)
    ev1.metric("Wall U-Value", f"{wall_u:.3f} W/m²K")
    ev2.metric("Roof U-Value", f"{roof_u:.3f} W/m²K")
    ev3.metric("Window-to-Wall Ratio", f"{wwr_percent:.1f}%")
    ev4.metric("Envelope Score", f"{env_score}/100")

    st.subheader("Roof Insulation & Glass Performance")

    ev5, ev6, ev7 = st.columns(3)
    ev5.metric("Roof Insulation R", f"{roof_ins_r:.2f} m²K/W")
    ev6.metric("Glass SHGC", f"{glass_shgc:.2f}")
    ev7.metric("Glass Status", glass_performance)

    st.subheader("Shading Device Estimate")

    sh1, sh2 = st.columns(2)
    sh1.metric("Window Height", f"{window_height:.2f} m")
    sh2.metric("Suggested Horizontal Shading Depth", f"{required_shading_depth:.2f} m")


with tab_designer:

    st.subheader("Designer Concept Sizing Tools")

    dtab1, dtab2, dtab3, dtab4, dtab5 = st.tabs([
        "HVAC Sizing",
        "Ventilation",
        "Electrical",
        "Water & Pump",
        "Solar + Battery"
    ])

    with dtab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Cooling Load", f"{concept_cooling_kw:.1f} kW")
        c2.metric("Cooling Load", f"{concept_cooling_tr:.1f} TR")
        c3.metric("AHU Airflow", f"{total_ahu_cfm:,.0f} CFM")

    with dtab2:
        v1, v2 = st.columns(2)
        v1.metric("Total Fresh Air", f"{total_fresh_air_cfm:,.0f} CFM")
        v2.metric("Fresh Air/person", f"{cfm_per_person:.1f} CFM/person")

    with dtab3:
        ee1, ee2, ee3 = st.columns(3)
        ee1.metric("Demand Load", f"{demand_kw:.1f} kW")
        ee2.metric("Transformer", f"{design_transformer_kva:.1f} kVA")
        ee3.metric("DG Set", f"{design_dg_kva:.1f} kVA")

    with dtab4:
        w1, w2, w3, w4, w5 = st.columns(5)
        w1.metric("Daily Water", f"{daily_water_demand:,.0f} L/day")
        w2.metric("UG Tank", f"{ug_tank_liters:,.0f} L")
        w3.metric("OH Tank", f"{oh_tank_liters:,.0f} L")
        w4.metric("Pump", f"{pump_kw:.2f} kW")
        w5.metric("Pump", f"{pump_hp:.2f} HP")

    with dtab5:
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("Solar Required", f"{required_kwp_design:.1f} kWp")
        s2.metric("Panel Count", f"{panel_count:.0f} Nos")
        s3.metric("Roof Required", f"{roof_area_required:.0f} m²")
        s4.metric("Roof Capacity", f"{roof_capacity_kwp:.1f} kWp")
        s5.metric("Battery", f"{design_battery_kwh:.1f} kWh")

        st.metric("Solar Inverter Size", f"{inverter_kw:.1f} kW")


with tab_weather:

    st.subheader("Weather & Psychrometric Analysis")

    ps1, ps2, ps3, ps4 = st.columns(4)
    ps1.metric("Outdoor Humidity Ratio", f"{outdoor_w:.4f} kg/kg")
    ps2.metric("Indoor Humidity Ratio", f"{indoor_w:.4f} kg/kg")
    ps3.metric("Outdoor Dew Point", f"{outdoor_dp:.1f} °C")
    ps4.metric("Indoor Dew Point", f"{indoor_dp:.1f} °C")

    ps5, ps6, ps7, ps8 = st.columns(4)
    ps5.metric("Outdoor Enthalpy", f"{outdoor_h:.1f} kJ/kg")
    ps6.metric("Indoor Enthalpy", f"{indoor_h:.1f} kJ/kg")
    ps7.metric("Fresh Air Load", f"{fresh_air_kw:.1f} kW")
    ps8.metric("Fresh Air Load", f"{fresh_air_tr:.1f} TR")


with tab_hvac_adv:

    st.subheader("Advanced HVAC Concept Sizing")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Sensible Load", f"{sensible_kw:.1f} kW")
    a2.metric("Fresh Air Load", f"{fresh_air_kw:.1f} kW")
    a3.metric("Total HVAC Load", f"{total_hvac_kw:.1f} kW")
    a4.metric("Total Cooling Load", f"{total_hvac_tr:.1f} TR")

    st.subheader("Duct Sizing")

    d1, d2 = st.columns(2)
    d1.metric("Duct Area", f"{duct_area_ft2:.2f} ft²")
    d2.metric("Equivalent Round Duct", f"{round_duct_mm:.0f} mm")

    st.subheader("Chilled Water & Pump Sizing")

    p1, p2, p3 = st.columns(3)
    p1.metric("CHW Flow", f"{chw_flow_gpm:.0f} GPM")
    p2.metric("CHW Flow", f"{chw_flow_m3hr:.1f} m³/hr")
    p3.metric("CHW Pump Power", f"{chw_pump_kw:.1f} kW")

    st.subheader("Cooling Tower Sizing")

    st.metric("Cooling Tower Capacity", f"{ct_tr:.1f} TR")


with tab_electrical:

    st.subheader("Electrical Detailed Design")

    e1, e2, e3 = st.columns(3)
    e1.metric("Full Load Current", f"{elec_current:.1f} A")
    e2.metric("Recommended Cable", cable)
    e3.metric("Breaker Size", f"{breaker} A")

    e4, e5, e6 = st.columns(3)
    e4.metric("Voltage Drop", f"{vd:.2f} V")
    e5.metric("Capacitor Bank", f"{kvar:.1f} kVAr")
    e6.metric("DG Set Size", f"{dg:.1f} kVA")

    st.metric("Panel Rating", f"{panel} A")


with tab_final:

    st.subheader("Fire Fighting Design")

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Total Fire Flow", f"{fire_total_flow:,.0f} LPM")
    f2.metric("Fire Tank", f"{fire_tank_kl:.1f} KL")
    f3.metric("Fire Pump", f"{fire_pump_hp:.1f} HP")
    f4.metric("Jockey Pump", f"{jockey_flow_lpm:.1f} LPM")

    st.subheader("Plumbing, STP & Rainwater")

    p1, p2, p3 = st.columns(3)
    p1.metric("STP Capacity", f"{stp_kld:.1f} KLD")
    p2.metric("Rainwater Harvesting", f"{rainwater_kl:.1f} KL/event")
    p3.metric("Hot Water Demand", f"{hot_water_liters:,.0f} L/day")

    st.subheader("Waste, Biogas & ESG")

    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Daily Waste", f"{daily_waste_kg:.1f} kg/day")
    w2.metric("Organic Waste", f"{organic_waste_kg:.1f} kg/day")
    w3.metric("Biogas Potential", f"{biogas_m3_day:.1f} m³/day")
    w4.metric("ESG Score", f"{building_esg_score}/100")

    st.subheader("Carbon Impact")

    st.metric("CO₂ Avoided by Solar", f"{solar_co2_avoided_tons:.1f} tons/year")


with tab_net_zero:

    st.subheader("Net Zero Energy Balance")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=min(net_zero_coverage, 150),
        title={"text": "Renewable Coverage (%)"},
        gauge={
            "axis": {"range": [0, 150]},
            "bar": {"color": "green"},
            "steps": [
                {"range": [0, 50], "color": "lightcoral"},
                {"range": [50, 100], "color": "khaki"},
                {"range": [100, 150], "color": "lightgreen"}
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": 100
            }
        }
    ))

    st.plotly_chart(fig, width="stretch")

    if net_zero_balance >= 0:
        st.success(f"Net Zero Achieved. Surplus energy: {net_zero_balance:,.0f} kWh/year")
    else:
        st.warning(f"Net Zero Gap: {abs(net_zero_balance):,.0f} kWh/year")


with tab_status:

    st.subheader("Performance Status")

    status_data = {
        "Parameter": [
            "EPI",
            "Passive Design",
            "Envelope",
            "Net Zero Coverage",
            "CO₂ Level",
            "Water Consumption",
            "HVAC Efficiency",
            "Lighting Power Density",
            "Power Factor",
            "Fresh Air Load",
            "Total HVAC Load"
        ],
        "Value": [
            f"{epi:.1f} kWh/m²/year",
            f"{passive_score}/100",
            f"{env_score}/100",
            f"{net_zero_coverage:.1f}%",
            f"{co2_ppm:.0f} ppm",
            f"{water_lpd:.0f} L/person/day",
            f"{kw_per_tr:.2f} kW/TR",
            f"{lighting_w_m2:.1f} W/m²",
            f"{power_factor:.2f}",
            f"{fresh_air_tr:.1f} TR",
            f"{total_hvac_tr:.1f} TR"
        ],
        "Status": [
            "Warning" if epi > 150 else "Pass",
            "Warning" if passive_score < 60 else "Pass",
            "Warning" if env_score < 60 else "Pass",
            "Gap" if net_zero_coverage < 100 else "Net Zero",
            "Warning" if co2_ppm > 1000 else "Pass",
            "Warning" if water_lpd > 135 else "Pass",
            hvac_status,
            lighting_status,
            "Warning" if power_factor < 0.95 else "Pass",
            "Review" if fresh_air_tr > 50 else "Normal",
            "Review"
        ]
    }

    df_status = pd.DataFrame(status_data)
    st.dataframe(df_status, width="stretch")

    st.subheader("Engineering Recommendations")

    for item in recommendations:
        st.write(f"- {item}")


with tab_report:

    st.subheader("Executive Net Zero Report")

    st.write(f"""
**{building_name}** consumes approximately **{annual_kwh:,.0f} kWh/year** with annual energy cost of 
**₹ {annual_cost:,.0f}**.

Residual load after expected reduction: **{reduced_load:,.0f} kWh/year**.

Renewable generation: **{solar_generation:,.0f} kWh/year**.

**Net Zero Balance = Generated Energy - Consumed Energy = {net_zero_balance:,.0f} kWh/year**

Designer and MEP outputs:

- Concept Cooling Load: **{concept_cooling_tr:.1f} TR**
- Advanced HVAC Load: **{total_hvac_tr:.1f} TR**
- Fresh Air Load: **{fresh_air_tr:.1f} TR**
- AHU Airflow: **{total_ahu_cfm:,.0f} CFM**
- Equivalent Round Duct: **{round_duct_mm:.0f} mm**
- CHW Flow: **{chw_flow_gpm:.0f} GPM**
- CHW Pump Power: **{chw_pump_kw:.1f} kW**
- Cooling Tower: **{ct_tr:.1f} TR**
- Transformer: **{design_transformer_kva:.1f} kVA**
- DG Set: **{design_dg_kva:.1f} kVA**
- UG Tank: **{ug_tank_liters:,.0f} Litres**
- OH Tank: **{oh_tank_liters:,.0f} Litres**
- Fire Tank: **{fire_tank_kl:.1f} KL**
- Fire Pump: **{fire_pump_hp:.1f} HP**
- STP Capacity: **{stp_kld:.1f} KLD**
- Solar Required: **{required_kwp_design:.1f} kWp**
- Battery: **{design_battery_kwh:.1f} kWh**
- ESG Score: **{building_esg_score}/100**

Estimated annual saving: **₹ {annual_saving:,.0f}**  
Simple payback: **{payback_years:.2f} years**
""")

    st.subheader("Download PDF Report")

    report_data = {
        "building_name": building_name,
        "building_type": building_type,
        "annual_kwh": annual_kwh,
        "annual_cost": annual_cost,
        "epi": epi,
        "co2_tons": co2_tons,
        "reduced_load": reduced_load,
        "solar_generation": solar_generation,
        "net_zero_coverage": net_zero_coverage,
        "net_zero_balance": net_zero_balance,
        "total_hvac_tr": total_hvac_tr,
        "fresh_air_tr": fresh_air_tr,
        "total_ahu_cfm": total_ahu_cfm,
        "design_transformer_kva": design_transformer_kva,
        "design_dg_kva": design_dg_kva,
        "stp_kld": stp_kld,
        "fire_tank_kl": fire_tank_kl,
        "fire_pump_hp": fire_pump_hp,
        "building_esg_score": building_esg_score,
        "solar_co2_avoided_tons": solar_co2_avoided_tons,
        "annual_saving": annual_saving,
        "payback_years": payback_years,
    }

    if st.button("Generate PDF Report"):
        pdf_file = generate_pdf_report("netzero_report.pdf", report_data)

        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Download Report PDF",
                data=file,
                file_name="netzero_building_report.pdf",
                mime="application/pdf"
            )
