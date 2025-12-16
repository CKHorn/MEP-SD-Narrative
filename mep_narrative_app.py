import streamlit as st
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import base64

# Page configuration
st.set_page_config(page_title="MEP SD Narrative Editor", layout="wide", page_icon="📋")

# Initialize session state
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'building_name': 'XXXXXXXXXX Building',
        'total_tonnage': 'XXX',
        'space_type_a': 'XXX Space Type A',
        'space_type_a_tonnage': 'XXX',
        'space_type_b': 'XXX Space Type B',
        'space_type_b_tonnage': 'XXX',
        'space_type_c': 'XXX Space Type C',
        'space_type_c_tonnage': 'XXX',
        'hvac_system_type': 'split_dx',
        'cooling_tower_gpm': 'XXXX',
        'chiller_tonnage': 'XXX',
        'vrf_tonnage': 'XXX',
        'outside_air_cfm': 'XXXXX',
        'parking_ventilation': 'mechanical',
        'domestic_water_size': '3"',
        'service_size': '2000',
        'generator_required': True,
        'lightning_protection': False,
        'solar_panels': False,
    }

def create_word_document(data):
    """Generate Word document from form data"""
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Title
    title = doc.add_heading(data['building_name'], level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Subtitle
    subtitle = doc.add_heading('MEP Schematic Design Narrative', level=1)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Introduction
    doc.add_paragraph()
    intro = doc.add_paragraph()
    intro_run = intro.add_run(
        'Mechanical, Electrical, Plumbing, & fire protection engineering design approach'
    )
    intro_run.bold = True
    
    doc.add_paragraph(
        f'The following scope outlines the design approach that shall be used for the '
        f'{data["building_name"]} building project for the Mechanical, Electrical, '
        f'Plumbing, & Fire Protection, Systems.'
    )
    
    # MECHANICAL SECTION
    doc.add_heading('MECHANICAL', level=1)
    
    # A. Codes and Standards
    doc.add_heading('A. Codes and Standards:', level=2)
    para = doc.add_paragraph('The building shall be provided with systems in accordance to:')
    codes = [
        '2020 Florida Building Code',
        '2020 Florida Mechanical Code',
        '2020 Florida Energy Code',
        '2020 Florida Plumbing Code',
        '2020 Florida Fuel Gas Code',
        'NFPA 88A, 92, 96, 101'
    ]
    for code in codes:
        doc.add_paragraph(code, style='List Bullet')
    
    # B. Design Conditions
    doc.add_heading('B. Design Conditions:', level=2)
    conditions = [
        'Summer Outside: 92°F DB/ 79°F WB',
        'Winter Outside: 43°F',
        'Summer Inside: 75°F DB/ 55%RH',
        'Winter Inside: 70°F'
    ]
    for condition in conditions:
        doc.add_paragraph(condition, style='List Bullet')
    
    # G. Building HVAC Systems
    doc.add_heading('G. Building HVAC Systems:', level=2)
    doc.add_paragraph(f'The total building tonnage is estimated at {data["total_tonnage"]} total tons:')
    doc.add_paragraph(f'{data["space_type_a_tonnage"]} Total tons for {data["space_type_a"]}:', style='List Bullet')
    doc.add_paragraph(f'{data["space_type_b_tonnage"]} Total tons for {data["space_type_b"]}:', style='List Bullet')
    doc.add_paragraph(f'{data["space_type_c_tonnage"]} Total tons for {data["space_type_c"]}:', style='List Bullet')
    
    # HVAC System Type
    hvac_systems = {
        'split_dx': 'H. Split Dx Systems:',
        'condenser_water': 'Condenser Water System:',
        'chilled_water': 'Chilled water System with Cooling Towers:',
        'vrf': 'Variable Refrigerant Flow System:'
    }
    
    doc.add_heading(hvac_systems.get(data['hvac_system_type'], 'H. Split Dx Systems:'), level=2)
    
    if data['hvac_system_type'] == 'split_dx':
        split_dx_content = [
            'The HVAC system will be made up of multiple split dx heat pump systems ranging from 1.5 tons to 5 tons.',
            'All condensing units shall be mounted on X" roof curb (or) roof support rails mounted a min. 18" off roof as per the Florida building code chapter 15 table 1510.10.',
            'All condensers shall be coated with a min. 4000 hr salt resistance coating.',
            'All condensers shall be hurricane strapped to structure.',
        ]
        for content in split_dx_content:
            doc.add_paragraph(content, style='List Bullet')
    
    # PLUMBING SECTION
    doc.add_heading('PLUMBING', level=1)
    
    doc.add_heading('A. Codes and Standards:', level=2)
    doc.add_paragraph('The building shall be provided with systems in accordance with:')
    plumb_codes = [
        '2017 Florida Building Code',
        '2017 Florida Mechanical Code',
        '2017 Florida Energy Code',
        '2017 Florida Plumbing Code',
        '2017 Florida Fuel Gas Code',
        'Americans with Disabilities Act (ADA)'
    ]
    for code in plumb_codes:
        doc.add_paragraph(code, style='List Bullet')
    
    doc.add_heading('B. Domestic Water:', level=2)
    doc.add_paragraph(
        f'A new domestic water service shall be extended and brought into each building from the existing main. '
        f'The building domestic water shall be {data["domestic_water_size"]} in size and enter the building '
        f'in the 1st level domestic water and fire pump room.'
    )
    
    # FIRE PROTECTION SECTION
    doc.add_heading('FIRE PROTECTION', level=1)
    
    doc.add_heading('A. Codes and Standards:', level=2)
    doc.add_paragraph(
        'Fire suppressions systems shall be designed and installed to meet the requirements '
        'of all applicable state and local codes as well as required industry standards as follows:'
    )
    fp_codes = [
        '2020 Florida Building Code (FBC)',
        '2020 Florida Fire Prevention Code (FFPC)',
        'NFPA 13 v.2016 -- Standard for the Installation of Sprinkler Systems',
        'NFPA 14 v.2016 -- Standard for the Installation of Standpipe and Hose Systems'
    ]
    for code in fp_codes:
        doc.add_paragraph(code, style='List Bullet')
    
    # ELECTRICAL SECTION
    doc.add_heading('ELECTRICAL', level=1)
    
    doc.add_heading('A. Codes and Standards:', level=2)
    doc.add_paragraph('2017 National Electrical Code NEC (NFPA 70)', style='List Bullet')
    
    doc.add_heading('B. Power Distribution:', level=2)
    doc.add_paragraph(
        f'A new electrical service from the utility Duke Energy will be designed to provide power to the building. '
        f'It is anticipated the service lateral will terminate in a {data["service_size"]}A switchboard.'
    )
    
    if data['generator_required']:
        doc.add_heading('C. Emergency Power Distribution:', level=2)
        doc.add_paragraph(
            'An Engine Generator Set for emergency power will be provided for the building. '
            'Emergency power will be distributed via circuit breaker-type distribution panels.'
        )
    
    # SOLAR PANELS (if selected)
    if data['solar_panels']:
        doc.add_heading('ROOF TOP SOLAR PANEL SYSTEM (ADD ALTERNATE)', level=1)
        solar_content = [
            'The proposed building will provide an option for roof mounted solar.',
            'The roof mounted solar PV system will consist of approximately 230 REC380AA panels that are 380 watts a piece with a 21.7% efficiency.',
            'The total size of the system would be 87 kW.',
        ]
        for content in solar_content:
            doc.add_paragraph(content, style='List Bullet')
    
    # FIRE ALARM SECTION
    doc.add_heading('FIRE ALARM', level=1)
    doc.add_heading('A. Codes and Standards:', level=2)
    fa_codes = [
        'Florida Fire Prevention Code NFPA 72',
        'The National Fire Alarm and Signaling Code',
        'NFPA 70 The National Electrical Code'
    ]
    for code in fa_codes:
        doc.add_paragraph(code, style='List Bullet')
    
    # Add closing
    doc.add_paragraph()
    doc.add_paragraph()
    closing = doc.add_paragraph('End of Narrative')
    closing.alignment = WD_ALIGN_PARAGRAPH.CENTER
    closing.runs[0].bold = True
    
    return doc

def get_download_link(doc, filename):
    """Generate download link for Word document"""
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

# Main App Layout
st.title("📋 MEP Schematic Design Narrative Editor")
st.markdown("---")

# Sidebar for key inputs
with st.sidebar:
    st.header("🏢 Project Information")
    st.session_state.form_data['building_name'] = st.text_input(
        "Building Name",
        value=st.session_state.form_data['building_name']
    )
    
    st.markdown("### System Selections")
    st.session_state.form_data['hvac_system_type'] = st.selectbox(
        "HVAC System Type",
        options=['split_dx', 'condenser_water', 'chilled_water', 'vrf'],
        format_func=lambda x: {
            'split_dx': 'Split DX Systems',
            'condenser_water': 'Condenser Water System',
            'chilled_water': 'Chilled Water System',
            'vrf': 'Variable Refrigerant Flow'
        }[x],
        index=['split_dx', 'condenser_water', 'chilled_water', 'vrf'].index(
            st.session_state.form_data['hvac_system_type']
        )
    )
    
    st.session_state.form_data['generator_required'] = st.checkbox(
        "Emergency Generator Required",
        value=st.session_state.form_data['generator_required']
    )
    
    st.session_state.form_data['solar_panels'] = st.checkbox(
        "Include Solar Panels (Add Alternate)",
        value=st.session_state.form_data['solar_panels']
    )
    
    st.session_state.form_data['lightning_protection'] = st.checkbox(
        "Lightning Protection",
        value=st.session_state.form_data['lightning_protection']
    )
    
    st.markdown("---")
    
    # Export button
    if st.button("📥 Generate & Download Word Document", type="primary", use_container_width=True):
        doc = create_word_document(st.session_state.form_data)
        doc_bytes = get_download_link(doc, "MEP_Narrative.docx")
        
        st.download_button(
            label="⬇️ Download Word Document",
            data=doc_bytes,
            file_name=f"{st.session_state.form_data['building_name'].replace(' ', '_')}_MEP_Narrative.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        st.success("✅ Document generated successfully!")

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔧 Mechanical", "💧 Plumbing", "⚡ Electrical", "🔥 Fire Protection"])

with tab1:
    st.header("Mechanical Systems")
    
    with st.expander("📊 Building HVAC Systems", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.form_data['total_tonnage'] = st.text_input(
                "Total Building Tonnage",
                value=st.session_state.form_data['total_tonnage']
            )
            st.session_state.form_data['space_type_a'] = st.text_input(
                "Space Type A Description",
                value=st.session_state.form_data['space_type_a']
            )
            st.session_state.form_data['space_type_a_tonnage'] = st.text_input(
                "Space Type A Tonnage",
                value=st.session_state.form_data['space_type_a_tonnage']
            )
        with col2:
            st.session_state.form_data['space_type_b'] = st.text_input(
                "Space Type B Description",
                value=st.session_state.form_data['space_type_b']
            )
            st.session_state.form_data['space_type_b_tonnage'] = st.text_input(
                "Space Type B Tonnage",
                value=st.session_state.form_data['space_type_b_tonnage']
            )
            st.session_state.form_data['space_type_c'] = st.text_input(
                "Space Type C Description",
                value=st.session_state.form_data['space_type_c']
            )
            st.session_state.form_data['space_type_c_tonnage'] = st.text_input(
                "Space Type C Tonnage",
                value=st.session_state.form_data['space_type_c_tonnage']
            )
    
    with st.expander("🌡️ Design Conditions"):
        st.info("Summer Outside: 92°F DB/ 79°F WB | Winter Outside: 43°F | Summer Inside: 75°F DB/ 55%RH | Winter Inside: 70°F")
    
    with st.expander("🏗️ Building Envelope Criteria"):
        st.info("Based on 2020 Florida Building Code, Energy Conservation, prescriptive minimums for Climate Zone 2A")
    
    with st.expander("💨 Outside Air System"):
        st.session_state.form_data['outside_air_cfm'] = st.text_input(
            "Outside Air CFM",
            value=st.session_state.form_data['outside_air_cfm']
        )
        st.write("Outside air will be provided via roof top units with energy recovery")
    
    with st.expander("🅿️ Parking Ventilation"):
        st.session_state.form_data['parking_ventilation'] = st.radio(
            "Parking Ventilation Type",
            options=['mechanical', 'open_air'],
            format_func=lambda x: 'Mechanical Ventilation (NFPA 88A)' if x == 'mechanical' else 'Open Air Garage',
            index=0 if st.session_state.form_data['parking_ventilation'] == 'mechanical' else 1
        )

with tab2:
    st.header("Plumbing Systems")
    
    with st.expander("💧 Domestic Water", expanded=True):
        st.session_state.form_data['domestic_water_size'] = st.text_input(
            "Domestic Water Service Size",
            value=st.session_state.form_data['domestic_water_size']
        )
        st.write("A new domestic water service shall be extended and brought into each building from the existing main.")
    
    with st.expander("🚽 Plumbing Fixtures"):
        st.write("**Public and General Fixtures**")
        st.write("- Fixtures shall be ADA compliant where required")
        st.write("- Lavatories: 0.4 gallons per minute maximum sensor activated")
        st.write("- Urinals: 0.85 gallons per flush (Pint Flush) maximum")
        st.write("- Water closets: 1.28 maximum gallons per flush")
    
    with st.expander("⚙️ Plumbing Equipment"):
        st.write("- Packaged duplex domestic water booster pump required")
        st.write("- Water sub-meters for each retail tenant unit and office levels")
        st.write("- Simplex submersible sump pump for each elevator pit")
    
    with st.expander("🌧️ Storm Drainage"):
        st.write("- Roof drains with overflow drains for secondary drainage")
        st.write("- Underground piping: PVC DWV pipe and fittings")
        st.write("- Rainwater collection system with retention vault")

with tab3:
    st.header("Electrical Systems")
    
    with st.expander("⚡ Power Distribution", expanded=True):
        st.session_state.form_data['service_size'] = st.text_input(
            "Service Size (Amps)",
            value=st.session_state.form_data['service_size']
        )
        st.write(f"Main service: {st.session_state.form_data['service_size']}A @ 480V/277VAC 3ɸ")
        st.write("- Duke Energy pad-mount transformer")
        st.write("- 480V for mechanical equipment")
        st.write("- 277V for lighting")
        st.write("- 208/120V for receptacles and residential units")
    
    with st.expander("💡 Lighting System"):
        st.write("**Illumination Levels (average maintained):**")
        st.write("- Lobbies and Corridors: 20 fc")
        st.write("- Restrooms: 25 fc")
        st.write("- Mechanical/Electrical Rooms: 25 fc")
        st.write("- Circulation Stairs: 10 fc")
    
    with st.expander("🔌 Wiring Devices"):
        st.write("- Specification grade: Hubbell, Pass & Seymour, Cooper")
        st.write("- GFCI receptacles per NEC requirements")
        st.write("- 20A, 120V branch circuits: 1500W maximum")
    
    if st.session_state.form_data['generator_required']:
        with st.expander("🔋 Emergency Power Distribution"):
            st.write("- Engine Generator Set (Caterpillar, Cummins, MTU)")
            st.write("- Automatic transfer switches (Zenith, Asco)")
            st.write("- Life safety loads")
            st.write("- Legally required standby loads")
            st.write("- Optional standby systems")

with tab4:
    st.header("Fire Protection & Fire Alarm Systems")
    
    with st.expander("🚿 Automatic Sprinkler/Standpipe Systems", expanded=True):
        st.write("- Automatic sprinkler systems throughout per FBC 403.3")
        st.write("- Class I standpipes in each egress stairwell")
        st.write("- Electric fire pump: 100 psi residual pressure")
        st.write("- Variable frequency drive controller with bypass")
    
    with st.expander("🔔 Fire Alarm System"):
        st.write("- Emergency voice alarm fire alarm system")
        st.write("- Main fire alarm control panel in fire command center")
        st.write("- Manual pull stations at all exits")
        st.write("- Smoke detection in mechanical, electrical, elevator rooms")
        st.write("- Speaker strobes throughout with separate paging zones")
        st.write("- Integration with smoke control systems")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>MEP SD Narrative Editor | Export to Word with one click</p>
    </div>
    """,
    unsafe_allow_html=True
)