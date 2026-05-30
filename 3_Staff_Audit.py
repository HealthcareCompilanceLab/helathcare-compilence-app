import streamlit as st
from auth import require_access
from utils import (
    apply_custom_style,
    render_hero,
    render_sidebar,
    render_kpi_card,
    render_section_header,
    render_progress_bar,
)

st.set_page_config(page_title="Staff Audit", page_icon="🩺", layout="wide")
apply_custom_style()
require_access("staff")

render_sidebar(st.session_state.user, None, None)

render_hero(
    "Healthcare Staff Security Audit",
    "Assess workforce security habits, privacy awareness, patient-data handling, and day-to-day healthcare security practices.",
    "Staff Review Mode"
)

sections = {
    "Authentication & Account Security": [
        ("Do you use MFA for healthcare systems that support it?", ["Yes, always", "Only for some systems", "No"], "MFA should be enabled to protect patient records and privileged access."),
        ("Do you ever share your password with coworkers or supervisors?", ["Never", "Only in urgent situations", "Yes"], "Password sharing increases insider threat and unauthorized access risks."),
        ("How do you handle password changes?", ["I change them when required or if compromise is suspected", "I wait for the system to force a reset", "I rarely or never change them"], "Passwords should be changed immediately if compromise is suspected and according to policy."),
        ("Do you use the same password for work systems and personal accounts?", ["Never", "Sometimes", "Yes"], "Password reuse increases the impact of credential compromise."),
    ],
    "Phishing & Communication Safety": [
        ("How confident are you in identifying phishing emails or fake login pages?", ["Very confident and I verify suspicious messages", "Somewhat confident", "Not confident"], "Additional phishing awareness training is recommended."),
        ("Do you report suspicious emails, calls, or texts to IT or Security immediately?", ["Yes, always", "Sometimes", "No"], "Suspicious communications should be reported immediately to IT or Security teams."),
        ("Have you completed cybersecurity awareness training recently?", ["Yes, within the last 12 months", "More than 12 months ago", "No"], "Regular cybersecurity awareness training should be mandatory."),
        ("Before clicking links in messages about scheduling, payroll, or patient records, what do you do?", ["I verify the sender or source first", "I usually click if it looks work-related", "I click without checking"], "Links related to schedules, payroll, or records should be verified before opening."),
    ],
    "Patient Data Handling": [
        ("Do you access patient records only when required for your job duties?", ["Yes, always", "Sometimes", "No"], "Access to patient records should follow least-privilege principles."),
        ("When discussing patient information, how do you protect privacy?", ["I speak privately and only with authorized staff", "I try to be careful but not always in private spaces", "I may discuss patient information where others can hear"], "Patient information should only be discussed privately with authorized personnel."),
        ("Do you ever write patient information on paper or personal notes without secure disposal?", ["Never", "Sometimes", "Yes, often"], "Patient information on paper must be protected and securely disposed of."),
        ("If you print documents containing patient information, what happens after use?", ["They are collected immediately and stored or shredded securely", "They may sit briefly in shared areas", "They are often left unattended"], "Printed records containing PHI should never be left unattended."),
    ],
    "Workstation & Device Security": [
        ("Do you leave workstations unlocked when unattended?", ["Never", "Sometimes", "Yes, often"], "Unlocked workstations may expose sensitive healthcare information."),
        ("Do you use personal USB devices on work systems?", ["Never", "Only with approval", "Yes"], "Unauthorized USB devices may introduce malware into healthcare systems."),
        ("How do you use mobile phones or tablets for patient-related work?", ["Only approved secure apps/devices are used", "Sometimes I use personal devices for convenience", "I regularly use personal apps or devices"], "Only approved secure devices and applications should be used for patient-related work."),
        ("If a shared workstation is still logged in under another user, what do you do?", ["Report it or lock/log out immediately", "Use it briefly if I am busy", "Continue using it without reporting"], "Shared or unattended logged-in sessions should be secured immediately."),
    ],
    "Clinical Workflow & Incident Response": [
        ("If you send patient-related information electronically, how is it shared?", ["Through approved secure systems only", "Sometimes through regular email or messaging if urgent", "Through whatever method is most convenient"], "Patient-related information should only be shared using approved secure channels."),
        ("If you notice someone accessing records they may not need, what do you do?", ["Report it immediately", "I might mention it informally", "I would probably ignore it"], "Potential inappropriate access to records should be reported immediately."),
        ("If a device used for work is lost or stolen, when should it be reported?", ["Immediately", "At the end of the shift", "Only if data loss is confirmed"], "Lost or stolen work devices should be reported immediately."),
        ("How often do you verify patient identity before discussing records, giving updates, or handling documentation?", ["Always", "Most of the time", "Not consistently"], "Patient identity should be verified consistently before handling sensitive information."),
    ]
}

question_total = sum(len(qs) for qs in sections.values())

x, y, z = st.columns(3)
with x:
    render_kpi_card("Assessment Scope", str(question_total), "Healthcare-specific control questions", "info")
with y:
    render_kpi_card("Review Areas", str(len(sections)), "Authentication, privacy, devices, incidents", "success")
with z:
    render_kpi_card("Audience", "Clinical Staff", "Built for healthcare workers handling PHI", "warning")

render_section_header("Audit Guidance", "Answer based on normal day-to-day practice, not ideal behavior.", "✦")

st.markdown("""
<div class="hc-card">
    <div class="hc-subtitle">
        This assessment reviews how healthcare workers protect patient information, use shared systems safely, respond to suspicious activity, and follow secure workflows in clinical environments.
    </div>
</div>
""", unsafe_allow_html=True)

score = 0
recommendations = []
section_scores = {}

with st.form("staff_audit_form"):
    answers = []

    for section_title, questions in sections.items():
        render_section_header(section_title, "Select the response that best reflects actual current behavior.", "▸")
        for question, options, issue in questions:
            answer = st.selectbox(question, options, key=question)
            answers.append((section_title, answer, options, issue))

    submitted = st.form_submit_button("Generate Staff Audit Report")

if submitted:
    total = len(answers)

    for section_title, answer, options, issue in answers:
        section_scores.setdefault(section_title, {"score": 0, "max": 0})
        section_scores[section_title]["max"] += 2

        if answer == options[0]:
            score += 2
            section_scores[section_title]["score"] += 2
        elif answer == options[1]:
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

    render_section_header("Assessment Results", "Visual summary of workforce cyber hygiene and privacy-safe behavior.", "✓")

    a, b = st.columns(2)
    with a:
        render_kpi_card("Security Awareness Score", f"{percent:.2f}%", "Based on behavior across all healthcare work patterns.", tone)
    with b:
        render_kpi_card("Risk Level", risk, "Reflects current workforce handling of security and PHI.", tone)

    st.markdown('<div class="hc-card">', unsafe_allow_html=True)
    for section_name, values in section_scores.items():
        section_pct = (values["score"] / values["max"]) * 100 if values["max"] else 0
        bar_tone = "success" if section_pct >= 80 else "warning" if section_pct >= 50 else "danger"
        render_progress_bar(section_name, section_pct, bar_tone)
    st.markdown('</div>', unsafe_allow_html=True)

    render_section_header("Recommendations", "Items that need coaching, policy reinforcement, or workflow correction.", "⚑")

    if recommendations:
        seen = set()
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                st.markdown(f'<div class="hc-alert">{rec}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hc-success">Excellent healthcare security practices detected.</div>', unsafe_allow_html=True)