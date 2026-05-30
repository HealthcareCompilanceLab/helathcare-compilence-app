from pathlib import Path
import streamlit as st
from auth import require_access
from utils import (
    load_json,
    compute_compliance,
    apply_custom_style,
    render_hero,
    render_sidebar,
    render_system_overview,
    render_kpi_card,
    render_section_header,
    render_progress_bar,
    render_findings_cards,
)

st.set_page_config(page_title="Compliance Officer", page_icon="📋", layout="wide")
apply_custom_style()
require_access("compliance")

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / "control_bank.json")
system = load_json(BASE_DIR / "system_data.json")
summary = compute_compliance(controls, system)

render_sidebar(st.session_state.user, summary, system)

render_hero(
    "Compliance Officer Review",
    "Review control mappings, evidence, remediation guidance, and overall compliance posture.",
    "Compliance Review"
)

a, b, c = st.columns(3)
with a:
    render_kpi_card("Compliance Score", f"{summary['percent']:.2f}%", "Overall measured posture", "info")
with b:
    render_kpi_card("Controls Reviewed", str(len(summary["results"])), "Mapped policy and technical checks", "success")
with c:
    render_kpi_card("Overall Risk", summary["overall"], "Current compliance exposure", "danger" if summary["overall"] == "HIGH RISK" else "warning" if summary["overall"] == "MEDIUM RISK" else "success")

render_section_header("Compliance Posture", "High-level review of control outcomes and evidence quality.", "◈")
st.markdown('<div class="hc-card">', unsafe_allow_html=True)
render_progress_bar("Compliance Readiness", summary["percent"], "info")
pass_rate = (summary["passed"] / len(summary["results"]) * 100) if summary["results"] else 0
fail_rate = (summary["failed"] / len(summary["results"]) * 100) if summary["results"] else 0
render_progress_bar("Passed Controls", pass_rate, "success")
render_progress_bar("Failed Controls", fail_rate, "danger")
st.markdown('</div>', unsafe_allow_html=True)

render_section_header("System Context", "Underlying technical state that supports control evidence.", "⬢")
render_system_overview(system)

render_section_header("Detailed Control Review", "Structured evidence, risk level, and remediation guidance.", "▣")
render_findings_cards(summary["results"])