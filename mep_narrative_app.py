import io
import streamlit as st
from docx import Document

st.set_page_config(page_title="MEP Narrative Editor", layout="wide")
st.title("MEP Narrative Editor (DOCX)")

st.caption(
    "Upload a .docx narrative, edit the text, then download an updated .docx. "
    "Note: this re-exports as text paragraphs (complex formatting/tables/images may not be preserved)."
)

# ----------------------------
# DOCX helpers
# ----------------------------
def docx_to_text(doc: Document) -> str:
    """Extract paragraph text to a single editable string."""
    parts = []
    for p in doc.paragraphs:
        parts.append(p.text)
    return "\n".join(parts).rstrip()

def text_to_docx_bytes(text: str) -> bytes:
    """
    Create a new DOCX from plain text.
    Blank lines become paragraph breaks.
    """
    out_doc = Document()

    # Split into paragraphs while preserving blank lines
    lines = text.splitlines()
    # Combine consecutive non-blank lines into paragraphs, but keep blank lines as paragraph separators
    para = []
    for line in lines:
        if line.strip() == "":
            # flush current paragraph
            if para:
                out_doc.add_paragraph("\n".join(para).rstrip())
                para = []
            else:
                # extra blank line -> empty paragraph
                out_doc.add_paragraph("")
        else:
            para.append(line)

    if para:
        out_doc.add_paragraph("\n".join(para).rstrip())

    buf = io.BytesIO()
    out_doc.save(buf)
    return buf.getvalue()

# ----------------------------
# UI
# ----------------------------
uploaded = st.file_uploader("Upload narrative DOCX", type=["docx"])

if "narrative_text" not in st.session_state:
    st.session_state["narrative_text"] = ""

if uploaded is not None:
    # Load and extract text
    try:
        doc = Document(uploaded)
        st.session_state["narrative_text"] = docx_to_text(doc)
        st.success("Loaded DOCX. Edit below.")
    except Exception as e:
        st.error(f"Could not read DOCX: {e}")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Edit Narrative")
    st.session_state["narrative_text"] = st.text_area(
        "Narrative text",
        value=st.session_state["narrative_text"],
        height=650,
        help="Edits here will be saved into a new DOCX as paragraphs.",
        label_visibility="collapsed",
    )

with col2:
    st.subheader("Tools")
    st.write("**Quick actions**")
    if st.button("Clear text"):
        st.session_state["narrative_text"] = ""

    st.divider()
    st.write("**Download**")

    filename = st.text_input("Output filename", value="MEP_Narrative_Edited.docx")

    if st.session_state["narrative_text"].strip():
        out_bytes = text_to_docx_bytes(st.session_state["narrative_text"])
        st.download_button(
            "⬇️ Download Edited DOCX",
            data=out_bytes,
            file_name=filename if filename.lower().endswith(".docx") else f"{filename}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    else:
        st.info("Add or load narrative text to enable download.")
