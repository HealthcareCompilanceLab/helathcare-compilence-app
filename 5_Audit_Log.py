from pathlib import Path
import streamlit as st
from auth import require_any_access
from utils import (
    load_json,
    compute_compliance,
    apply_custom_style,
    render_hero,
    render_sidebar,
    read_audit_log,
)

st.set_page_config(page_title="Audit Log", page_icon="📜", layout="wide")
apply_custom_style()
require_any_access(["admin", "it", "compliance"])

BASE_DIR = Path(__file__).resolve().parent.parent
controls = load_json(BASE_DIR / "control_bank.json")
system = load_json(BASE_DIR / "system_data.json")
summary = compute_compliance(controls, system)

render_sidebar(st.session_state.user, summary, system)

render_hero(
    "Login Audit Log",
    "Review login and logout events recorded by the compliance dashboard.",
    "Restricted Access"
)

log_lines = read_audit_log(limit=300)

success_count = sum("STATUS=SUCCESS" in line and "EVENT=LOGIN" in line for line in log_lines)
failed_count = sum("STATUS=FAILED" in line for line in log_lines)
logout_count = sum("EVENT=LOGOUT" in line for line in log_lines)

a, b, c = st.columns(3)
with a:
    st.metric("Successful Logins", success_count)
with b:
    st.metric("Failed Logins", failed_count)
with c:
    st.metric("Logouts", logout_count)

st.markdown("""
<div class="hc-card">
    <div class="hc-card-title">Audit Log Records</div>
    <div class="hc-subtitle">
        Latest authentication events captured in the system log file.
    </div>
</div>
""", unsafe_allow_html=True)

if log_lines:
    file_data = "\n".join(reversed(log_lines))
    st.download_button(
        "Download Audit Log TXT",
        data=file_data,
        file_name="login_audit_log.txt",
        mime="text/plain"
    )
    st.code("\n".join(log_lines), language="text")
else:
    st.markdown(
        '<div class="hc-success">No audit log entries have been recorded yet.</div>',
        unsafe_allow_html=True
    )