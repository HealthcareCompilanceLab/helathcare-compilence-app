from pathlib import Path
import streamlit as st
from auth import require_access
from utils import (
    load_json,
    compute_compliance,
    apply_custom_style,
    render_hero,
    render_alerts,
    render_sidebar,
    render_system_overview,
    render_kpi_card,
    render_section_header,
    render_progress_bar,
    render_findings_cards,
)

st.set_page_config(page_title="Admin Dashboard", page_icon="🛡️", layout="wide")
apply_custom_style()
require_access("admin")

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / "control_bank.json")
system = load_json(BASE_DIR / "system_data.json")
summary = compute_compliance(controls, system)

render_sidebar(st.session_state.user, summary, system)

render_hero(
    "Admin Dashboard",
    "Full compliance visibility, technical findings, alerts, and healthcare security posture in one place.",
    "Admin Access"
)

a, b, c, d = st.columns(4)
with a:
    render_kpi_card("Compliance Score", f"{summary['percent']:.2f}%", "Overall control alignment", "info")
with b:
    render_kpi_card("Risk Level", summary["overall"], "Current environment exposure", "danger" if summary["overall"] == "HIGH RISK" else "warning" if summary["overall"] == "MEDIUM RISK" else "success")
with c:
    render_kpi_card("Passed Controls", str(summary["passed"]), "Controls currently compliant", "success")
with d:
    render_kpi_card("Failed Controls", str(summary["failed"]), "Controls requiring attention", "danger")

render_section_header("Posture Overview", "Visual breakdown of compliance and operational security health.", "◈")

st.markdown('<div class="hc-card">', unsafe_allow_html=True)
render_progress_bar("Compliance Readiness", summary["percent"], "info")
pass_rate = (summary["passed"] / len(summary["results"]) * 100) if summary["results"] else 0
fail_rate = (summary["failed"] / len(summary["results"]) * 100) if summary["results"] else 0
render_progress_bar("Passed Controls", pass_rate, "success")
render_progress_bar("Failed Controls", fail_rate, "danger")
st.markdown('</div>', unsafe_allow_html=True)

render_section_header("System Intelligence", "Current technical safeguards and attack-surface signals.", "⬢")
render_system_overview(system)

render_section_header("Security Alerts", "Automated detections and authentication anomalies requiring visibility.", "⚠")
render_alerts(summary["alerts"])

render_section_header("Control Findings", "Structured view of compliance gaps, evidence, and remediation actions.", "▣")
render_findings_cards(summary["results"])