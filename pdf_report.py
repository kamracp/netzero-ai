from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def generate_pdf_report(filename, data):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 25 * mm

    def line(text, size=10, gap=7):
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(20 * mm, y, str(text))
        y -= gap * mm
        if y < 25 * mm:
            c.showPage()
            y = height - 25 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, "Net Zero Building Digital Twin Report")
    y -= 12 * mm

    line(f"Building Name: {data.get('building_name', '')}", 11)
    line(f"Building Type: {data.get('building_type', '')}", 11)
    line("")

    line("Energy Performance", 13, 9)
    line(f"Annual Energy: {data.get('annual_kwh', 0):,.0f} kWh/year")
    line(f"Annual Cost: Rs. {data.get('annual_cost', 0):,.0f}/year")
    line(f"EPI: {data.get('epi', 0):.1f} kWh/m2/year")
    line(f"CO2 Emission: {data.get('co2_tons', 0):.1f} tons/year")
    line("")

    line("Net Zero & Renewable", 13, 9)
    line(f"Reduced Load: {data.get('reduced_load', 0):,.0f} kWh/year")
    line(f"Solar Generation: {data.get('solar_generation', 0):,.0f} kWh/year")
    line(f"Net Zero Coverage: {data.get('net_zero_coverage', 0):.1f}%")
    line(f"Net Zero Balance: {data.get('net_zero_balance', 0):,.0f} kWh/year")
    line("")

    line("MEP Outputs", 13, 9)
    line(f"Cooling Load: {data.get('total_hvac_tr', 0):.1f} TR")
    line(f"Fresh Air Load: {data.get('fresh_air_tr', 0):.1f} TR")
    line(f"AHU Airflow: {data.get('total_ahu_cfm', 0):,.0f} CFM")
    line(f"Transformer: {data.get('design_transformer_kva', 0):.1f} kVA")
    line(f"DG Set: {data.get('design_dg_kva', 0):.1f} kVA")
    line("")

    line("Fire / Water / ESG", 13, 9)
    line(f"STP Capacity: {data.get('stp_kld', 0):.1f} KLD")
    line(f"Fire Tank: {data.get('fire_tank_kl', 0):.1f} KL")
    line(f"Fire Pump: {data.get('fire_pump_hp', 0):.1f} HP")
    line(f"ESG Score: {data.get('building_esg_score', 0)}/100")
    line(f"CO2 Avoided by Solar: {data.get('solar_co2_avoided_tons', 0):.1f} tons/year")
    line("")

    line("ROI", 13, 9)
    line(f"Annual Saving: Rs. {data.get('annual_saving', 0):,.0f}/year")
    line(f"Simple Payback: {data.get('payback_years', 0):.2f} years")
    line("")

    line("Note", 13, 9)
    line("This is a preliminary concept-level engineering report.")
    line("Final design must be validated with site survey, local codes and vendor data.")

    c.save()
    return filename