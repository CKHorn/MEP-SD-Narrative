import io
import json
from dataclasses import dataclass
from typing import Dict, List

import streamlit as st
from docx import Document

st.set_page_config(page_title="MEP Narrative Builder", layout="wide")
st.title("MEP Narrative Builder — Structured Sections + Toggles")

# ============================================================
# Narrative Model
# ============================================================
@dataclass
class BulletItem:
    key: str
    label: str
    text: str
    default_on: bool = True

@dataclass
class SectionSpec:
    key: str
    title: str
    intro_default: str
    bullets: List[BulletItem]

# ---- Edit these to match your template structure ----
SECTIONS: List[SectionSpec] = [
    SectionSpec(
        key="project_overview",
        title="Project Overview",
        intro_default=(
            "Provide a brief description of the project, scope, and overall MEP design intent."
        ),
        bullets=[
            BulletItem("ov_coord", "Coordination approach", "Coordinate with Architect, Structural, Civil, and Owner/Client team.", True),
            BulletItem("ov_codes", "Code compliance statement", "Design will comply with applicable codes and authority having jurisdiction requirements.", True),
            BulletItem("ov_sustain", "Sustainability / energy goals", "Incorporate energy-efficient strategies consistent with project goals.", False),
        ],
    ),
    SectionSpec(
        key="design_criteria",
        title="Design Criteria",
        intro_default="Describe basis of design criteria, assumptions, and design constraints.",
        bullets=[
            BulletItem("dc_loads", "Load assumptions", "Loads based on preliminary architectural program and typical tenant usage.", True),
            BulletItem("dc_coord", "Design coordination", "Ongoing coordination with project stakeholders throughout design phases.", True),
            BulletItem("dc_allow", "Allowances / exclusions", "Specific scope items and exclusions to be confirmed during SD.", False),
        ],
    ),
    SectionSpec(
        key="electrical",
        title="Electrical Narrative",
        intro_default="Summarize electrical systems and design approach.",
        bullets=[
            BulletItem("el_service", "Utility service", "Confirm utility service requirements and service point location with the serving utility.", True),
            BulletItem("el_distribution", "Distribution concept", "Develop distribution system concept including main distribution, feeders, and panels.", True),
            BulletItem("el_lighting", "Lighting & controls", "Coordinate lighting layout assumptions and controls narrative; comply with energy code.", True),
            BulletItem("el_lifesafety", "Life safety / emergency", "Develop emergency power and life safety systems approach per code and AHJ requirements.", True),
            BulletItem("el_ev", "EV charging", "Coordinate EV charging assumptions and infrastructure requirements.", False),
        ],
    ),
    SectionSpec(
        key="plumbing",
        title="Plumbing Narrative",
        intro_default="Summarize plumbing systems and design approach.",
        bullets=[
            BulletItem("pl_sanvent", "Sanitary / vent", "Develop sanitary and vent system concepts including risers and coordination with architectural shafts.", True),
            BulletItem("pl_domestic", "Domestic water", "Develop domestic hot/cold water distribution concepts; coordinate equipment sizing.", True),
            BulletItem("pl_storm", "Storm drainage", "Develop roof and site storm drainage concepts including primary/overflow strategy.", True),
            BulletItem("pl_grease", "Grease waste (if applicable)", "Include grease waste strategy where food service or similar program exists.", False),
            BulletItem("pl_garage", "Garage drainage (if applicable)", "Include garage drainage strategy including collection and discharge approach.", False),
            BulletItem("pl_podium", "Podium coordination (if applicable)", "Include podium storm and coordination tasks if podium is part of project.", False),
        ],
    ),
    SectionSpec(
        key="fire_protection",
        title="Fire Protection Narrative",
        intro_default="Summarize fire protection design approach (if in scope).",
        bullets=[
            BulletItem("fp_basis", "Basis of design", "Confirm system type and design criteria with applicable code and Owner requirements.", True),
            BulletItem("fp_coord", "Coordination", "Coordinate fire protection routing and impacts with architectural and structural systems.", True),
            BulletItem("fp_hyd", "Hydraulic calculations", "Prepare hydraulic calculations as required for permitting and final design.", False),
        ],
    ),
    SectionSpec(
        key="mechanical",
        title="Mechanical Narrative",
        intro_default="Summarize mechanical systems and design approach.",
        bullets=[
            BulletItem("me_loads", "IES Loads", "Develop loads consistent with energy model / IES assumptions and equipment selections.", True),
            BulletItem("me_oa", "OA Calcs", "Establish outdoor air requirements and ventilation strategy per code.", True),
            BulletItem("me_duct", "Ductwork", "Develop ductwork distribution concepts, sizing, and coordination with structure/ceilings.", True),
            BulletItem("me_ref", "Refrigerant piping", "Develop refrigerant piping routing and coordination where DX systems are used.", False),
            BulletItem("me_smoke", "Smoke control", "Develop smoke control approach where required by code and AHJ.", False),
            BulletItem("me_chw", "Chilled water", "Develop chilled water distribution and equipment concepts where applicable.", False),
            BulletItem("me_cw", "Condenser water", "Develop condenser water distribution and equipment concepts where applicable.", False),
        ],
    ),
    SectionSpec(
        key="coordination_deliverables",
        title="Coordination & Deliverables",
        intro_default="Summarize deliverables and coordination milestones.",
        bullets=[
            BulletItem("cd_meetings", "Meetings", "Attend coordination meetings and respond to project communications.", True),
            BulletItem("cd_reviews", "QA/QC", "Perform internal QA/QC reviews at key milestones.", True),
            BulletItem("cd_permit", "Permitting support", "Support permitting/plan review comments and revise documents accordingly.", True),
        ],
    ),
]

# ============================================================
# State Init
# ============================================================
def init_state():
    if "sections" not in st.session_state:
        st.session_state.sections = {}
        for sec in SECTIONS:
            st.session_state.sections[sec.key] = {
                "intro": sec.intro_default,
                "bullets": {b.key: b.default_on for b in sec.bullets},
                "custom_bullets": [],  # list[str]
            }
    if "project_meta" not in st.session_state:
        st.session_state.project_meta = {
            "project_name": "",
            "project_location": "",
            "prepared_for": "",
            "prepared_by": "",
            "date": "",
        }

init_state()

# ============================================================
# JSON Save/Load
# ============================================================
def export_json() -> str:
    payload = {
        "project_meta": st.session_state.project_meta,
        "sections": st.session_state.sections,
    }
    return json.dumps(payload, indent=2)

def import_json(s: str):
    obj = json.loads(s)
    if "project_meta" in obj:
        st.session_state.project_meta.update(obj["project_meta"])
    if "sections" in obj:
        # merge, keep unknown keys if present
        for k, v in obj["sections"].items():
            st.session_state.sections[k] = v

# ============================================================
# DOCX Export
# ============================================================
def build_docx_bytes() -> bytes:
    doc = Document()

    pm = st.session_state.project_meta

    doc.add_heading("MEP SD Narrative", level=1)
    if pm.get("project_name"):
        doc.add_paragraph(f"Project: {pm['project_name']}")
    if pm.get("project_location"):
        doc.add_paragraph(f"Location: {pm['project_location']}")
    if pm.get("prepared_for"):
        doc.add_paragraph(f"Prepared For: {pm['prepared_for']}")
    if pm.get("prepared_by"):
        doc.add_paragraph(f"Prepared By: {pm['prepared_by']}")
    if pm.get("date"):
        doc.add_paragraph(f"Date: {pm['date']}")

    doc.add_paragraph("")

    for sec in SECTIONS:
        data = st.session_state.sections.get(sec.key, {})
        intro = (data.get("intro") or "").strip()
        bullets_state: Dict[str, bool] = data.get("bullets", {})
        custom_bullets: List[str] = data.get("custom_bullets", [])

        doc.add_heading(sec.title, level=2)

        if intro:
            doc.add_paragraph(intro)

        # Standard bullets
        for b in sec.bullets:
            if bool(bullets_state.get(b.key, False)):
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(b.text)

        # Custom bullets
        for cb in custom_bullets:
            cb = (cb or "").strip()
            if cb:
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(cb)

        doc.add_paragraph("")

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# ============================================================
# Sidebar: Project Meta + Save/Load
# ============================================================
with st.sidebar:
    st.header("Project Info")
    pm = st.session_state.project_meta
    pm["project_name"] = st.text_input("Project Name", value=pm.get("project_name", ""))
    pm["project_location"] = st.text_input("Project Location", value=pm.get("project_location", ""))
    pm["prepared_for"] = st.text_input("Prepared For", value=pm.get("prepared_for", ""))
    pm["prepared_by"] = st.text_input("Prepared By", value=pm.get("prepared_by", ""))
    pm["date"] = st.text_input("Date", value=pm.get("date", ""))

    st.divider()
    st.header("Save / Load (JSON)")

    json_str = export_json()
    st.download_button(
        "⬇️ Download JSON",
        data=json_str.encode("utf-8"),
        file_name="mep_narrative.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_json = st.file_uploader("Load JSON", type=["json"])
    if uploaded_json is not None:
        try:
            import_json(uploaded_json.read().decode("utf-8"))
            st.success("Loaded JSON.")
        except Exception as e:
            st.error(f"Could not load JSON: {e}")

    st.divider()
    st.header("DOCX Export")
    out_name = st.text_input("DOCX filename", value="MEP_SD_Narrative.docx")
    st.download_button(
        "⬇️ Download DOCX",
        data=build_docx_bytes(),
        file_name=out_name if out_name.lower().endswith(".docx") else f"{out_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )

# ============================================================
# Main UI: Section Editor
# ============================================================
st.subheader("Sections")

for sec in SECTIONS:
    data = st.session_state.sections[sec.key]

    with st.expander(sec.title, expanded=(sec.key in ["project_overview", "electrical", "plumbing", "mechanical"])):
        st.markdown("**Section text**")
        data["intro"] = st.text_area(
            f"{sec.title} intro",
            value=data.get("intro", ""),
            height=110,
            key=f"intro_{sec.key}",
            label_visibility="collapsed",
        )

        st.markdown("**Toggle bullets**")
        if sec.bullets:
            cols = st.columns(2)
            for i, b in enumerate(sec.bullets):
                c = cols[i % 2]
                data["bullets"][b.key] = c.checkbox(
                    b.label,
                    value=bool(data["bullets"].get(b.key, b.default_on)),
                    key=f"bullet_{sec.key}_{b.key}",
                )
        else:
            st.caption("No bullets configured for this section.")

        st.markdown("**Custom bullets**")
        # Add custom bullet input
        new_cb = st.text_input(f"Add a custom bullet to {sec.title}", value="", key=f"newcb_{sec.key}")
        add_col, clear_col = st.columns([1, 1])
        if add_col.button("Add bullet", key=f"addcb_{sec.key}"):
            if new_cb.strip():
                data["custom_bullets"].append(new_cb.strip())
                st.session_state[f"newcb_{sec.key}"] = ""  # clear input

        if clear_col.button("Clear custom bullets", key=f"clearcb_{sec.key}"):
            data["custom_bullets"] = []

        # Show existing custom bullets
        if data["custom_bullets"]:
            for idx, cb in enumerate(list(data["custom_bullets"])):
                row = st.columns([0.9, 0.1])
                row[0].write(f"• {cb}")
                if row[1].button("✕", key=f"delcb_{sec.key}_{idx}"):
                    data["custom_bullets"].pop(idx)
                    st.rerun()

# ============================================================
# Live Preview
# ============================================================
st.divider()
st.subheader("Preview")

preview_lines: List[str] = []
pm = st.session_state.project_meta
if pm.get("project_name"):
    preview_lines.append(f"# MEP SD Narrative — {pm['project_name']}")
else:
    preview_lines.append("# MEP SD Narrative")

for sec in SECTIONS:
    data = st.session_state.sections.get(sec.key, {})
    intro = (data.get("intro") or "").strip()
    bullets_state = data.get("bullets", {})
    custom_bullets = data.get("custom_bullets", [])

    preview_lines.append(f"\n## {sec.title}")
    if intro:
        preview_lines.append(intro)

    for b in sec.bullets:
        if bool(bullets_state.get(b.key, False)):
            preview_lines.append(f"- {b.text}")

    for cb in custom_bullets:
        cb = (cb or "").strip()
        if cb:
            preview_lines.append(f"- {cb}")

st.markdown("\n".join(preview_lines))
