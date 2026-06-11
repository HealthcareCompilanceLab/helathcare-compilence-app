from pathlib import Path
import streamlit as st
from auth import authenticate_user, initialize_session, logout, user_has_access
from utils import (
    load_json,
    compute_compliance,
    apply_custom_style,
    render_hero,
    render_alerts,
    render_sidebar,
    render_system_overview,
    append_audit_log,
)

st.set_page_config(page_title="Healthcare Compliance App", page_icon="🏥", layout="wide")
apply_custom_style()

BASE_DIR = Path(__file__).resolve().parent
EMPLOYEE_FILE = BASE_DIR / "employees.json"
CONTROL_FILE = BASE_DIR / "control_bank.json"
SYSTEM_FILE = BASE_DIR / "system_data.json"

initialize_session()
employees = load_json(EMPLOYEE_FILE)
controls = load_json(CONTROL_FILE)
system = load_json(SYSTEM_FILE)
summary = compute_compliance(controls, system)

render_sidebar(st.session_state.user if st.session_state.user else None, summary, system)

render_hero(
    "Healthcare Security Command Center",
    "Real-time compliance visibility, workforce security posture, and infrastructure risk monitoring for healthcare environments.",
    "Secure Monitoring Active"
)

if not st.session_state.logged_in:
    st.markdown("""
    <div class="hc-card">
        <div class="hc-title" style="font-size:24px;">Employee Login</div>
        <div class="hc-subtitle">Access your dashboard using your Job ID and password.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        job_id = st.text_input("Job ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = authenticate_user(job_id, password, employees)
        if user:
            append_audit_log(
                event_type="LOGIN",
                status="SUCCESS",
                user=user,
                note="User logged into Streamlit dashboard"
            )
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome, {user['name']} ({user['role']})")
            st.rerun()
        else:
            append_audit_log(
                event_type="LOGIN",
                status="FAILED",
                attempted_job_id=job_id,
                note="Invalid credentials provided"
            )
            st.error("Invalid Job ID or password.")

    st.markdown("""
    <div class="hc-card">
        <div class="hc-card-title">Demo Accounts</div>
        <div class="hc-subtitle">
            <p><strong>EMP001 / admin123</strong> — Admin</p>
            <p><strong>EMP002 / itsecure123</strong> — IT Security</p>
            <p><strong>EMP003 / staff123</strong> — Healthcare Staff</p>
            <p><strong>EMP004 / compliance123</strong> — Compliance Officer</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    user = st.session_state.user

    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f"""
        <div class="hc-card">
            <div class="hc-title" style="font-size:24px;">Welcome, {user['name']}</div>
            <div class="hc-subtitle">
                <strong>Job ID:</strong> {user['job_id']}<br>
                <strong>Role:</strong> {user['role']}<br>
                <strong>Department:</strong> {user['department']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.write("")
        st.write("")
        if st.button("Logout"):
            append_audit_log(
                event_type="LOGOUT",
                status="SUCCESS",
                user=user,
                note="User logged out of Streamlit dashboard"
            )
            logout()
            st.rerun()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Compliance Score", f"{summary['percent']:.2f}%")
    col2.metric("Risk Level", summary["overall"])
    col3.metric("Passed Controls", summary["passed"])
    col4.metric("Failed Controls", summary["failed"])

    risk_class = "hc-low" if summary["overall"] == "LOW RISK" else "hc-medium" if summary["overall"] == "MEDIUM RISK" else "hc-high"

    st.markdown(f"""
    <div class="hc-card">
        <div class="hc-card-title">Role-based Access</div>
        <div class="hc-subtitle">{", ".join(user.get("access", []))}</div>
        <br>
        <div class="hc-card-title">Current Risk Assessment</div>
        <div class="{risk_class}" style="font-size:28px;">{summary["overall"]}</div>
    </div>
    """, unsafe_allow_html=True)

    render_system_overview(system)

    st.markdown("### Security Alerts")
    render_alerts(summary["alerts"])

    st.markdown("### What this role can access")
    if user_has_access(user, "admin"):
        st.markdown('<div class="hc-success">Full access to compliance, alerts, employee views, and system data.</div>', unsafe_allow_html=True)
    elif user_has_access(user, "it"):
        st.markdown('<div class="hc-success">Access to security controls, alerts, attack indicators, and remediation data.</div>', unsafe_allow_html=True)
    elif user_has_access(user, "staff"):
        st.markdown('<div class="hc-success">Access to staff audit questions and limited dashboard summary.</div>', unsafe_allow_html=True)
    elif user_has_access(user, "compliance"):
        st.markdown('<div class="hc-success">Access to compliance mappings, control status, and reporting summaries.</div>', unsafe_allow_html=True)