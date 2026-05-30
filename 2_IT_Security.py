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

st.set_page_config(page_title="IT Security", page_icon="💻", layout="wide")
apply_custom_style()
require_access("it")

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / "control_bank.json")
system = load_json(BASE_DIR / "system_data.json")
summary = compute_compliance(controls, system)

render_sidebar(st.session_state.user, summary, system)

render_hero(
    "IT Security Infrastructure Audit",
    "Review technical safeguards, monitoring maturity, encryption status, privileged access, and infrastructure resilience.",
    "IT Audit Mode"
)

x, y, z = st.columns(3)
with x:
    render_kpi_card("Security Controls", str(len(summary["results"])), "Monitored technical control checks", "info")
with y:
    render_kpi_card("Live Alerts", str(len(summary["alerts"])), "Current security detections", "warning" if summary["alerts"] else "success")
with z:
    render_kpi_card("Current Risk", summary["overall"], "Environment-wide security posture", "danger" if summary["overall"] == "HIGH RISK" else "warning" if summary["overall"] == "MEDIUM RISK" else "success")

render_section_header("Technical Posture", "Live infrastructure indicators and safeguard visibility.", "⬢")
render_system_overview(system)

st.markdown("""
<div class="hc-card">
    <div class="hc-card-title">Technical Visibility</div>
    <div class="hc-subtitle">
        Complete the audit below to assess implementation maturity across identity, monitoring, and infrastructure controls.
    </div>
</div>
""", unsafe_allow_html=True)

sections = {
    "Access Control & Authentication": [
        ("Is MFA enabled for privileged accounts?", "Privileged accounts should always use MFA protection."),
        ("Is Role-Based Access Control implemented?", "RBAC helps reduce excessive privilege exposure."),
        ("Are inactive accounts automatically disabled?", "Inactive accounts should be disabled to reduce unauthorized access risks."),
    ],
    "Logging & Monitoring": [
        ("Is audit logging enabled?", "Audit logs are required for healthcare compliance investigations."),
        ("Are logs reviewed regularly?", "Regular log review improves threat detection and incident response."),
        ("Is a SIEM platform deployed?", "SIEM deployment improves centralized monitoring and alerting."),
    ],
    "Infrastructure Security": [
        ("Are backups encrypted?", "Healthcare backups should always be encrypted to protect PHI."),
        ("Is TLS/HTTPS enforced?", "Encrypted communication channels should be enforced organization-wide."),
        ("Are vulnerability scans performed monthly?", "Regular vulnerability scanning is critical for proactive security management."),
        ("Is endpoint protection installed?", "Endpoint protection helps reduce malware and ransomware risks."),
    ],
}

score = 0
recommendations = []
section_scores = {}

with st.form("it_audit_form"):
    answers = []
    for section_title, questions in sections.items():
        render_section_header(section_title, "Review actual implemented technical controls.", "▸")
        for question, issue in questions:
            answer = st.selectbox(
                question,
                ["Implemented", "Partial", "Not Implemented"],
                key=question
            )
            answers.append((section_title, answer, issue))

    submitted = st.form_submit_button("Generate IT Audit Report")

if submitted:
    total = len(answers)

    for section_title, answer, issue in answers:
        section_scores.setdefault(section_title, {"score": 0, "max": 0})
        section_scores[section_title]["max"] += 2

        if answer == "Implemented":
            score += 2
            section_scores[section_title]["score"] += 2
        elif answer == "Partial":
            score += 1
            section_scores[section_title]["score"] += 1
        else:
            recommendations.append(issue)

    percent = (score / (total * 2)) * 100 if total else 0

    if percent >= 80:
        risk = "LOW RISK"
        tone = "success"
    elif percent >= 50:
        risk = "MEDIUM RISK"
        tone = "warning"
    else:
        risk = "HIGH RISK"
        tone = "danger"

    render_section_header("IT Audit Results", "Maturity summary across key technical control domains.", "✓")

    c1, c2 = st.columns(2)
    with c1:
        render_kpi_card("IT Security Readiness", f"{percent:.2f}%", "Measured across authentication, monitoring, and infrastructure safeguards.", tone)
    with c2:
        render_kpi_card("Infrastructure Risk", risk, "Risk based on current IT audit responses.", tone)

    st.markdown('<div class="hc-card">', unsafe_allow_html=True)
    for section_name, values in section_scores.items():
        section_pct = (values["score"] / values["max"]) * 100 if values["max"] else 0
        bar_tone = "success" if section_pct >= 80 else "warning" if section_pct >= 50 else "danger"
        render_progress_bar(section_name, section_pct, bar_tone)
    st.markdown('</div>', unsafe_allow_html=True)

    render_section_header("Security Recommendations", "Implementation areas needing remediation or stronger technical enforcement.", "⚑")
    if recommendations:
        seen = set()
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                st.markdown(f'<div class="hc-alert">{rec}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="hc-success">Infrastructure security controls appear properly implemented.</div>',
            unsafe_allow_html=True
        )

render_section_header("Current Control Findings", "Current compliance evidence and remediation guidance for monitored controls.", "▣")
render_findings_cards(summary["results"])