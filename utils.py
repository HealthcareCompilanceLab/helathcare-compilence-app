import json
from pathlib import Path

RISK_WEIGHTS = {"High": 3, "Medium": 2, "Low": 1}


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_compliance(controls, system):
    results = []
    alerts = []
    score = 0
    max_score = 0
    passed = failed = insufficient = 0

    for control in controls:
        field = control["field"]
        risk = control["risk"]
        weight = RISK_WEIGHTS[risk]
        max_score += weight

        if field not in system:
            status = "INSUFFICIENT"
            insufficient += 1
            value = "Not Found"
        else:
            value = system[field]

            if control.get("comparison") == "min":
                status = "COMPLIANT" if value >= control["expected"] else "NON-COMPLIANT"
            else:
                status = "COMPLIANT" if value == control["expected"] else "NON-COMPLIANT"

            if status == "COMPLIANT":
                score += weight
                passed += 1
            else:
                failed += 1

        results.append({
            "id": control.get("id", "N/A"),
            "category": control.get("category", "Uncategorized"),
            "desc": control["description"],
            "status": status,
            "risk": risk,
            "remediation": control["remediation"],
            "evidence": f"{field} = {value}"
        })

    failed_logins = system.get("login_attempts", []).count("failed")

    if failed_logins >= 3:
        alerts.append("Multiple failed login attempts detected")

    if system.get("suspicious_ip_detected"):
        alerts.append("Suspicious IP detected")

    percent = (score / max_score) * 100 if max_score else 0

    if percent >= 80:
        overall = "LOW RISK"
    elif percent >= 50:
        overall = "MEDIUM RISK"
    else:
        overall = "HIGH RISK"

    return {
        "results": results,
        "alerts": alerts,
        "score": score,
        "max_score": max_score,
        "percent": percent,
        "overall": overall,
        "passed": passed,
        "failed": failed,
        "insufficient": insufficient,
    }


def apply_custom_style():
    import streamlit as st

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 24%),
            radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 28%),
            radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.08), transparent 24%),
            linear-gradient(135deg, #06101f 0%, #0b1324 45%, #111827 100%);
        color: #e5eefc;
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1240px;
    }

    h1, h2, h3 {
        color: #f8fbff !important;
    }

    .hc-hero {
        background: rgba(15, 23, 42, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.16);
        backdrop-filter: blur(18px);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.22);
        margin-bottom: 24px;
    }

    .hc-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 30px;
        color: #f8fbff !important;
        letter-spacing: 0.03em;
        margin-bottom: 8px;
    }

    .hc-subtitle {
        color: #94a3b8 !important;
        font-size: 14px;
        line-height: 1.6;
    }

    .hc-pill {
        display: inline-block;
        margin-top: 14px;
        padding: 10px 16px;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.12);
        color: #22c55e !important;
        border: 1px solid rgba(34, 197, 94, 0.34);
        font-size: 13px;
        font-weight: 700;
    }

    .hc-card {
        background: rgba(15, 23, 42, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.16);
        backdrop-filter: blur(16px);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
        margin-bottom: 18px;
    }

    .hc-card-title {
        color: #94a3b8 !important;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 12px;
        font-weight: 700;
    }

    .hc-score {
        font-size: 30px;
        font-weight: 800;
        color: #67e8f9 !important;
        text-shadow: 0 0 18px rgba(103, 232, 249, 0.12);
    }

    .hc-low { color: #22c55e !important; font-weight: 800; }
    .hc-medium { color: #facc15 !important; font-weight: 800; }
    .hc-high { color: #ef4444 !important; font-weight: 800; }

    .hc-alert {
        background: rgba(127, 29, 29, 0.30);
        color: #fecaca !important;
        padding: 15px;
        border: 1px solid rgba(248, 113, 113, 0.18);
        border-radius: 12px;
        margin-bottom: 12px;
    }

    .hc-success {
        background: rgba(22, 53, 28, 0.40);
        color: #bbf7d0 !important;
        border: 1px solid rgba(34, 197, 94, 0.18);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
    }

    .hc-info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 16px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .hc-mini-card {
        background: rgba(8, 17, 32, 0.80);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 16px;
        padding: 16px;
    }

    .hc-mini-label {
        font-size: 12px;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
        font-weight: 700;
    }

    .hc-mini-value {
        font-size: 24px;
        font-weight: 800;
        color: #f8fbff !important;
    }

    .hc-chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .hc-chip-ok {
        background: rgba(34, 197, 94, 0.12);
        color: #22c55e !important;
        border: 1px solid rgba(34, 197, 94, 0.28);
    }

    .hc-chip-warn {
        background: rgba(250, 204, 21, 0.12);
        color: #facc15 !important;
        border: 1px solid rgba(250, 204, 21, 0.28);
    }

    .hc-chip-danger {
        background: rgba(239, 68, 68, 0.12);
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.28);
    }

    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07111f 0%, #0a1729 45%, #0b1d33 100%) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.14) !important;
    }

    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #07111f 0%, #0a1729 45%, #0b1d33 100%) !important;
    }

    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #07111f 0%, #0a1729 45%, #0b1d33 100%) !important;
    }

    div[data-testid="stSidebarUserContent"] {
        background: transparent !important;
    }

    button[kind="header"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        background: transparent !important;
        color: #cfe7ff !important;
    }

    div[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }

    .hc-sidebar-brand {
        background: linear-gradient(180deg, rgba(14, 23, 42, 0.96), rgba(10, 18, 33, 0.92));
        border: 1px solid rgba(103, 232, 249, 0.16);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .hc-sidebar-brand h2 {
        font-family: 'Orbitron', sans-serif;
        color: #67e8f9 !important;
        font-size: 20px;
        margin: 0 0 8px 0;
        letter-spacing: 0.04em;
    }

    .hc-sidebar-brand p {
        color: #8ea7c2 !important;
        font-size: 12px;
        line-height: 1.55;
        margin: 0;
    }

    .hc-sidebar-box {
        background: rgba(14, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.11);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
    }

    .hc-sidebar-label {
        font-size: 11px;
        color: #7f94ab !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
        font-weight: 700;
    }

    .hc-sidebar-value {
        font-size: 13px;
        color: #e5eefc !important;
        font-weight: 600;
        line-height: 1.55;
        margin-bottom: 3px;
    }

    section[data-testid="stSidebarNav"] {
        background: rgba(10, 18, 33, 0.60) !important;
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 16px;
        padding: 10px 8px 8px 8px;
        margin-top: 10px;
    }

    section[data-testid="stSidebarNav"]::before {
        content: "Navigation";
        display: block;
        color: #7f94ab;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        padding: 4px 10px 10px 10px;
    }

    section[data-testid="stSidebarNav"] a {
        background: rgba(16, 27, 48, 0.78) !important;
        border: 1px solid rgba(56, 189, 248, 0.08);
        border-radius: 12px;
        padding: 10px 12px;
        color: #d8e6f5 !important;
    }

    section[data-testid="stSidebarNav"] a:hover {
        background: rgba(17, 40, 71, 0.88) !important;
        border-color: rgba(56, 189, 248, 0.20) !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.22);
        background: linear-gradient(90deg, #0891b2, #2563eb);
        color: white;
        box-shadow: 0 0 18px rgba(37, 99, 235, 0.16);
    }

    .stTextInput input, .stSelectbox select {
        background: rgba(8, 17, 32, 0.92) !important;
        color: #f8fbff !important;
        border-radius: 12px !important;
    }

    .stDataFrame, .stTable {
        background: rgba(8, 17, 32, 0.58);
        border-radius: 16px;
    }

    .hc-section-head {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 8px 0 18px 0;
        padding: 14px 16px;
        border-radius: 16px;
        background: rgba(10, 18, 33, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.12);
    }

    .hc-section-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(8,145,178,0.22), rgba(37,99,235,0.22));
        color: #67e8f9;
        font-size: 18px;
        font-weight: 800;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .hc-section-title {
        font-size: 18px;
        font-weight: 800;
        color: #f8fbff;
    }

    .hc-section-subtitle {
        font-size: 13px;
        color: #8ea7c2;
        margin-top: 2px;
    }

    .hc-kpi-card {
        position: relative;
        overflow: hidden;
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 16px;
        background: rgba(15, 23, 42, 0.64);
        border: 1px solid rgba(148, 163, 184, 0.14);
        box-shadow: 0 12px 28px rgba(0,0,0,0.22);
    }

    .hc-kpi-card::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.03), transparent 40%);
        pointer-events: none;
    }

    .hc-kpi-title {
        color: #8ea7c2;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .hc-kpi-value {
        font-size: 30px;
        font-weight: 800;
        color: #f8fbff;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    .hc-kpi-subtitle {
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.5;
    }

    .hc-kpi-info { border-color: rgba(56, 189, 248, 0.16); }
    .hc-kpi-success { border-color: rgba(34, 197, 94, 0.18); }
    .hc-kpi-warning { border-color: rgba(250, 204, 21, 0.18); }
    .hc-kpi-danger { border-color: rgba(239, 68, 68, 0.18); }

    .hc-progress-wrap {
        margin-bottom: 14px;
    }

    .hc-progress-label-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #dbeafe;
        font-size: 13px;
        margin-bottom: 7px;
    }

    .hc-progress-track {
        width: 100%;
        height: 10px;
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 999px;
        overflow: hidden;
    }

    .hc-progress-fill {
        height: 100%;
        border-radius: 999px;
        box-shadow: 0 0 18px rgba(255,255,255,0.08);
    }

    .hc-bar-info {
        background: linear-gradient(90deg, #06b6d4, #3b82f6);
    }

    .hc-bar-success {
        background: linear-gradient(90deg, #16a34a, #22c55e);
    }

    .hc-bar-warning {
        background: linear-gradient(90deg, #eab308, #facc15);
    }

    .hc-bar-danger {
        background: linear-gradient(90deg, #dc2626, #ef4444);
    }

    .hc-finding-card {
        background: rgba(15, 23, 42, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.20);
    }

    .hc-finding-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 14px;
    }

    .hc-finding-title {
        font-size: 18px;
        font-weight: 800;
        color: #f8fbff;
        line-height: 1.45;
    }

    .hc-finding-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
    }

    .hc-finding-box {
        background: rgba(8, 17, 32, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 14px;
        padding: 14px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero(title, subtitle, pill_text):
    import streamlit as st
    st.markdown(f"""
    <div class="hc-hero">
        <div class="hc-title">{title}</div>
        <div class="hc-subtitle">{subtitle}</div>
        <div class="hc-pill">{pill_text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_alerts(alerts):
    import streamlit as st
    if alerts:
        for alert in alerts:
            st.markdown(f'<div class="hc-alert">{alert}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hc-success">No active security alerts detected.</div>', unsafe_allow_html=True)


def render_sidebar(user=None, summary=None, system=None):
    import streamlit as st

    with st.sidebar:
        st.markdown("""
        <div class="hc-sidebar-brand">
            <h2>HC DASHBOARD</h2>
            <p>Healthcare security monitoring for compliance posture, workforce awareness, and infrastructure readiness.</p>
        </div>
        """, unsafe_allow_html=True)

        if user:
            st.markdown(f"""
            <div class="hc-sidebar-box">
                <div class="hc-sidebar-label">User</div>
                <div class="hc-sidebar-value">{user['name']}</div>
                <div class="hc-sidebar-value">{user['role']}</div>
                <div class="hc-sidebar-value">{user['department']}</div>
            </div>
            """, unsafe_allow_html=True)

        if summary:
            st.markdown(f"""
            <div class="hc-sidebar-box">
                <div class="hc-sidebar-label">Compliance Snapshot</div>
                <div class="hc-sidebar-value">Score: {summary['percent']:.2f}%</div>
                <div class="hc-sidebar-value">Risk: {summary['overall']}</div>
                <div class="hc-sidebar-value">Passed: {summary['passed']}</div>
                <div class="hc-sidebar-value">Failed: {summary['failed']}</div>
            </div>
            """, unsafe_allow_html=True)

        if system:
            failed_logins = system.get("login_attempts", []).count("failed")
            suspicious = "Detected" if system.get("suspicious_ip_detected") else "None"

            st.markdown(f"""
            <div class="hc-sidebar-box">
                <div class="hc-sidebar-label">System Watch</div>
                <div class="hc-sidebar-value">Failed Logins: {failed_logins}</div>
                <div class="hc-sidebar-value">Suspicious IP: {suspicious}</div>
                <div class="hc-sidebar-value">MFA: {"Enabled" if system.get("mfa_enabled") else "Disabled"}</div>
                <div class="hc-sidebar-value">TLS: {"Enabled" if system.get("tls_enabled") else "Disabled"}</div>
            </div>
            """, unsafe_allow_html=True)


def render_system_overview(system):
    import streamlit as st

    failed_logins = system.get("login_attempts", []).count("failed")
    suspicious = system.get("suspicious_ip_detected", False)

    st.markdown("""
    <div class="hc-card">
        <div class="hc-card-title">System Intelligence</div>
        <div class="hc-subtitle">Live technical posture and security control visibility from current system data.</div>
        <div class="hc-info-grid">
    """, unsafe_allow_html=True)

    cards = [
        ("MFA", "Enabled" if system.get("mfa_enabled") else "Disabled", "hc-low" if system.get("mfa_enabled") else "hc-high"),
        ("TLS / HTTPS", "Enabled" if system.get("tls_enabled") else "Disabled", "hc-low" if system.get("tls_enabled") else "hc-high"),
        ("Audit Logging", "Enabled" if system.get("logging_enabled") else "Disabled", "hc-low" if system.get("logging_enabled") else "hc-high"),
        ("Backup Encryption", "Enabled" if system.get("backup_encrypted") else "Disabled", "hc-low" if system.get("backup_encrypted") else "hc-high"),
        ("Password Length", str(system.get("password_length", "N/A")), "hc-low" if system.get("password_length", 0) >= 8 else "hc-medium"),
        ("Failed Logins", str(failed_logins), "hc-high" if failed_logins >= 3 else "hc-low"),
    ]

    for label, value, cls in cards:
        st.markdown(f"""
        <div class="hc-mini-card">
            <div class="hc-mini-label">{label}</div>
            <div class="hc-mini-value {cls}">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    chips = []
    chips.append('<span class="hc-chip hc-chip-ok">MFA Active</span>' if system.get("mfa_enabled") else '<span class="hc-chip hc-chip-danger">MFA Missing</span>')
    chips.append('<span class="hc-chip hc-chip-ok">TLS Protected</span>' if system.get("tls_enabled") else '<span class="hc-chip hc-chip-danger">TLS Disabled</span>')
    chips.append('<span class="hc-chip hc-chip-ok">Logging On</span>' if system.get("logging_enabled") else '<span class="hc-chip hc-chip-danger">Logging Off</span>')
    chips.append('<span class="hc-chip hc-chip-ok">Encrypted Backups</span>' if system.get("backup_encrypted") else '<span class="hc-chip hc-chip-danger">Backups Unencrypted</span>')
    chips.append('<span class="hc-chip hc-chip-danger">Suspicious IP Detected</span>' if suspicious else '<span class="hc-chip hc-chip-ok">No Suspicious IP</span>')
    chips.append('<span class="hc-chip hc-chip-warn">Password Policy Weak</span>' if system.get("password_length", 0) < 8 else '<span class="hc-chip hc-chip-ok">Password Policy Good</span>')

    st.markdown("".join(chips), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_kpi_card(title, value, subtitle="", tone="info"):
    import streamlit as st
    tone_class = {
        "info": "hc-kpi-info",
        "success": "hc-kpi-success",
        "warning": "hc-kpi-warning",
        "danger": "hc-kpi-danger"
    }.get(tone, "hc-kpi-info")

    st.markdown(f"""
    <div class="hc-kpi-card {tone_class}">
        <div class="hc-kpi-top">
            <div class="hc-kpi-title">{title}</div>
        </div>
        <div class="hc-kpi-value">{value}</div>
        <div class="hc-kpi-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title, subtitle="", icon="◆"):
    import streamlit as st
    st.markdown(f"""
    <div class="hc-section-head">
        <div class="hc-section-icon">{icon}</div>
        <div>
            <div class="hc-section-title">{title}</div>
            <div class="hc-section-subtitle">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(label, value, tone="info"):
    import streamlit as st
    pct = max(0, min(100, float(value)))
    tone_class = {
        "info": "hc-bar-info",
        "success": "hc-bar-success",
        "warning": "hc-bar-warning",
        "danger": "hc-bar-danger"
    }.get(tone, "hc-bar-info")

    st.markdown(f"""
    <div class="hc-progress-wrap">
        <div class="hc-progress-label-row">
            <span>{label}</span>
            <span>{pct:.0f}%</span>
        </div>
        <div class="hc-progress-track">
            <div class="hc-progress-fill {tone_class}" style="width:{pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_findings_cards(results):
    import streamlit as st
    for row in results:
        status = row["status"]
        if status == "COMPLIANT":
            badge_class = "hc-chip-ok"
        elif status == "NON-COMPLIANT":
            badge_class = "hc-chip-danger"
        else:
            badge_class = "hc-chip-warn"

        risk = row["risk"]
        risk_class = "hc-low" if risk == "Low" else "hc-medium" if risk == "Medium" else "hc-high"

        st.markdown(f"""
        <div class="hc-finding-card">
            <div class="hc-finding-top">
                <div>
                    <div class="hc-card-title">{row['id']} · {row['category']}</div>
                    <div class="hc-finding-title">{row['desc']}</div>
                </div>
                <div>
                    <span class="hc-chip {badge_class}">{status}</span>
                </div>
            </div>
            <div class="hc-finding-grid">
                <div class="hc-finding-box">
                    <div class="hc-sidebar-label">Risk</div>
                    <div class="{risk_class}" style="font-size:16px; font-weight:800;">{risk}</div>
                </div>
                <div class="hc-finding-box">
                    <div class="hc-sidebar-label">Evidence</div>
                    <div class="hc-sidebar-value">{row['evidence']}</div>
                </div>
                <div class="hc-finding-box">
                    <div class="hc-sidebar-label">Remediation</div>
                    <div class="hc-sidebar-value">{row['remediation']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)