import json
from pathlib import Path
import webbrowser


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
CONTROL_FILE = BASE_DIR / "control_bank.json"
SYSTEM_FILE = BASE_DIR / "system_data.json"
REPORT_FILE = BASE_DIR / "report.html"

risk_weights = {"High": 3, "Medium": 2, "Low": 1}


# =========================================================
# LOAD DATA
# =========================================================

with CONTROL_FILE.open("r", encoding="utf-8") as f:
    controls = json.load(f)

with SYSTEM_FILE.open("r", encoding="utf-8") as f:
    system = json.load(f)

results = []
alerts = []

score = 0
max_score = 0

passed = failed = insufficient = 0


# =========================================================
# COMPLIANCE CHECK
# =========================================================

for control in controls:
    field = control["field"]
    risk = control["risk"]
    weight = risk_weights[risk]

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
        "desc": control["description"],
        "status": status,
        "risk": risk,
        "remediation": control["remediation"],
        "evidence": f"{field} = {value}"
    })


# =========================================================
# ATTACK DETECTION
# =========================================================

failed_logins = system.get("login_attempts", []).count("failed")

if failed_logins >= 3:
    alerts.append("⚠ Multiple failed login attempts detected")

if system.get("suspicious_ip_detected"):
    alerts.append("🚨 Suspicious IP detected")


# =========================================================
# SCORE
# =========================================================

percent = (score / max_score) * 100 if max_score else 0

if percent >= 80:
    overall = "LOW RISK"
elif percent >= 50:
    overall = "MEDIUM RISK"
else:
    overall = "HIGH RISK"


# =========================================================
# HTML UI
# =========================================================

html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Healthcare Security Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700&display=swap" rel="stylesheet">
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

:root {{
    --bg-1: #06101f;
    --bg-2: #0b1324;
    --bg-3: #111827;
    --panel: rgba(15, 23, 42, 0.58);
    --border: rgba(148, 163, 184, 0.16);
    --text: #e5eefc;
    --muted: #94a3b8;
    --cyan: #67e8f9;
    --blue: #38bdf8;
    --violet: #a855f7;
    --green: #22c55e;
    --yellow: #facc15;
    --red: #ef4444;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    font-family: 'Inter', sans-serif;
    background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 25%),
        radial-gradient(circle at top right, rgba(168, 85, 247, 0.14), transparent 30%),
        radial-gradient(circle at bottom right, rgba(34, 211, 238, 0.10), transparent 25%),
        linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-3) 100%);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
}}

body::before {{
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 38px 38px;
    pointer-events: none;
    opacity: 0.20;
}}

.loading-screen {{
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 18px;
    background:
        radial-gradient(circle at top, rgba(56, 189, 248, 0.20), transparent 30%),
        linear-gradient(135deg, #040b16 0%, #091321 50%, #10182b 100%);
    transition: opacity 0.5s ease, visibility 0s ease;
}}

.loading-screen.hidden {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
}}

.loader-ring {{
    width: 86px;
    height: 86px;
    border-radius: 50%;
    border: 4px solid rgba(103, 232, 249, 0.14);
    border-top-color: var(--cyan);
    box-shadow: 0 0 24px rgba(103, 232, 249, 0.18);
    animation: spin 1s linear infinite;
}}

.loader-title {{
    font-family: 'Orbitron', sans-serif;
    font-size: 20px;
    letter-spacing: 0.08em;
    color: #e6faff;
    text-shadow: 0 0 18px rgba(103, 232, 249, 0.18);
}}

.loader-subtitle {{
    color: var(--muted);
    font-size: 13px;
}}

.sidebar {{
    width: 270px;
    height: 100vh;
    background: rgba(10, 18, 33, 0.75);
    -webkit-backdrop-filter: blur(18px);
    backdrop-filter: blur(18px);
    border-right: 1px solid var(--border);
    position: fixed;
    padding: 24px 18px;
    box-shadow: 0 0 40px rgba(0,0,0,0.28);
    z-index: 10;
    animation: slideInLeft 0.7s ease;
}}

.brand {{
    margin-bottom: 28px;
    padding: 16px;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(103, 232, 249, 0.12);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}}

.brand h2 {{
    font-family: 'Orbitron', sans-serif;
    color: var(--cyan);
    font-size: 21px;
    letter-spacing: 0.05em;
    text-shadow: 0 0 18px rgba(103, 232, 249, 0.30);
}}

.brand p {{
    margin-top: 8px;
    font-size: 12px;
    color: var(--muted);
    line-height: 1.5;
}}

.sidebar button {{
    width: 100%;
    padding: 14px 16px;
    margin-bottom: 14px;
    background: rgba(30, 41, 59, 0.45);
    color: var(--text);
    border: 1px solid rgba(56, 189, 248, 0.12);
    border-radius: 14px;
    cursor: pointer;
    transition: all 0.25s ease;
    text-align: left;
    font-weight: 600;
}}

.sidebar button:hover {{
    background: rgba(14, 165, 233, 0.14);
    border-color: rgba(56, 189, 248, 0.42);
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.16);
    transform: translateX(4px);
}}

.main {{
    margin-left: 290px;
    padding: 30px;
    animation: fadeUp 0.75s ease;
}}

.page-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 28px;
    padding: 24px;
    border-radius: 22px;
    background: var(--panel);
    -webkit-backdrop-filter: blur(18px);
    backdrop-filter: blur(18px);
    border: 1px solid var(--border);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.22);
    animation: fadeUp 0.85s ease;
}}

.page-title h1 {{
    font-family: 'Orbitron', sans-serif;
    font-size: 30px;
    color: #f8fbff;
    letter-spacing: 0.03em;
}}

.page-title p {{
    margin-top: 8px;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.6;
    max-width: 700px;
}}

.status-pill {{
    padding: 10px 16px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.12);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.34);
    font-size: 13px;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 0 0 18px rgba(34, 197, 94, 0.10);
}}

.card-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}}

.card {{
    position: relative;
    overflow: hidden;
    background: var(--panel);
    -webkit-backdrop-filter: blur(16px);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    padding: 22px;
    border-radius: 18px;
    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.03);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    animation: fadeUp 0.9s ease;
}}

.card::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(103, 232, 249, 0.08), transparent 35%, transparent 65%, rgba(168, 85, 247, 0.07));
    pointer-events: none;
}}

.card:hover {{
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.35);
    box-shadow:
        0 14px 34px rgba(0, 0, 0, 0.28),
        0 0 22px rgba(56, 189, 248, 0.10);
}}

.card h3 {{
    margin-bottom: 12px;
    color: var(--muted);
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.score {{
    font-size: 30px;
    font-weight: 800;
    color: var(--cyan);
    text-shadow: 0 0 18px rgba(103, 232, 249, 0.15);
}}

.metric-row {{
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 14px;
}}

.metric-block {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}

.metric-caption {{
    font-size: 12px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

.progress-card {{
    display: grid;
    grid-template-columns: 100px 1fr;
    align-items: center;
    gap: 18px;
}}

.progress-ring-wrap {{
    position: relative;
    width: 96px;
    height: 96px;
}}

.progress-ring {{
    width: 96px;
    height: 96px;
    transform: rotate(-90deg);
}}

.progress-ring.small {{
    width: 88px;
    height: 88px;
}}

.progress-ring circle {{
    fill: none;
    stroke-width: 8;
    stroke-linecap: round;
}}

.progress-ring .ring-bg {{
    stroke: rgba(148, 163, 184, 0.18);
}}

.progress-ring .ring-progress {{
    stroke: url(#ringGradient);
    stroke-dasharray: 263.89;
    stroke-dashoffset: 263.89;
    filter: drop-shadow(0 0 10px rgba(103, 232, 249, 0.28));
    transition: stroke-dashoffset 1.2s ease;
}}

.progress-value {{
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 800;
    color: #f8fbff;
}}

.progress-value.small {{
    font-size: 18px;
}}

.low {{
    color: #22c55e;
}}

.medium {{
    color: #facc15;
}}

.high {{
    color: #ef4444;
}}

.section {{
    background: var(--panel);
    -webkit-backdrop-filter: blur(16px);
    backdrop-filter: blur(16px);
    padding: 26px;
    border-radius: 20px;
    margin-bottom: 30px;
    border: 1px solid var(--border);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.20);
    animation: fadeUp 1s ease;
}}

.section h2 {{
    font-size: 22px;
    color: #f8fbff;
    margin-bottom: 8px;
}}

.section-subtitle {{
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 20px;
    line-height: 1.6;
}}

.results-table {{
    width: 100%;
    border-collapse: collapse;
    overflow: hidden;
    border-radius: 16px;
    background: rgba(8, 17, 32, 0.58);
}}

.results-table thead th {{
    background: rgba(8, 17, 32, 0.92);
    color: #dbeafe;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 16px;
    text-align: left;
    border-bottom: 1px solid #243041;
}}

.results-table tbody tr {{
    border-bottom: 1px solid rgba(148, 163, 184, 0.10);
    transition: background 0.2s ease;
}}

.results-table tbody tr:hover {{
    background: rgba(27, 41, 64, 0.55);
}}

.results-table td {{
    padding: 18px 16px;
    vertical-align: top;
    color: #e5e7eb;
}}

.control-title {{
    font-weight: 700;
    font-size: 16px;
    color: #f8fafc;
    margin-bottom: 6px;
}}

.control-note {{
    font-size: 13px;
    color: var(--muted);
}}

.badge {{
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.03em;
    white-space: nowrap;
}}

.badge-success {{
    background: rgba(34, 197, 94, 0.12);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.35);
    box-shadow: 0 0 14px rgba(34, 197, 94, 0.08);
}}

.badge-danger {{
    background: rgba(239, 68, 68, 0.12);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.35);
    box-shadow: 0 0 14px rgba(239, 68, 68, 0.06);
}}

.badge-warning {{
    background: rgba(250, 204, 21, 0.12);
    color: #facc15;
    border: 1px solid rgba(250, 204, 21, 0.35);
}}

.risk-low {{
    color: #22c55e;
    font-weight: 700;
}}

.risk-medium {{
    color: #facc15;
    font-weight: 700;
}}

.risk-high {{
    color: #ef4444;
    font-weight: 700;
}}

.evidence-box {{
    display: inline-block;
    background: rgba(8, 17, 32, 0.95);
    color: #93c5fd;
    border: 1px solid rgba(56, 189, 248, 0.18);
    border-radius: 10px;
    padding: 10px 12px;
    font-family: Consolas, monospace;
    font-size: 13px;
    line-height: 1.5;
}}

.remediation-box {{
    background: rgba(56, 189, 248, 0.08);
    border-left: 4px solid var(--blue);
    padding: 12px 14px;
    border-radius: 10px;
    color: #dbeafe;
    font-size: 14px;
    line-height: 1.5;
}}

.alert {{
    background: rgba(127, 29, 29, 0.35);
    color: #fecaca;
    padding: 15px;
    border: 1px solid rgba(248, 113, 113, 0.18);
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0 0 18px rgba(248, 113, 113, 0.05);
    animation: fadeUp 0.55s ease;
}}

.alert.success {{
    background: rgba(22, 53, 28, 0.45);
    color: #bbf7d0;
    border: 1px solid rgba(34, 197, 94, 0.18);
}}

label {{
    display: block;
    margin-top: 10px;
    margin-bottom: 8px;
    font-weight: 600;
    color: #e2e8f0;
}}

input, select {{
    width: 100%;
    padding: 13px 14px;
    margin-top: 8px;
    margin-bottom: 20px;
    background: rgba(8, 17, 32, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.18);
    color: #f8fbff;
    border-radius: 12px;
    outline: none;
    transition: all 0.25s ease;
}}

input:focus, select:focus {{
    border-color: rgba(56, 189, 248, 0.55);
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.14);
}}

.submit-btn {{
    background: linear-gradient(90deg, #06b6d4, #3b82f6);
    color: white;
    padding: 15px;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    width: 100%;
    font-size: 16px;
    font-weight: 700;
    box-shadow: 0 0 24px rgba(59, 130, 246, 0.18);
    transition: all 0.25s ease;
}}

.submit-btn:hover {{
    transform: translateY(-2px);
    box-shadow: 0 0 28px rgba(6, 182, 212, 0.24);
}}

.hidden {{
    display: none;
}}

.fade-in {{
    animation: fadeUp 0.6s ease;
}}

@keyframes fadeUp {{
    from {{
        opacity: 0;
        transform: translateY(16px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes slideInLeft {{
    from {{
        opacity: 0;
        transform: translateX(-25px);
    }}
    to {{
        opacity: 1;
        transform: translateX(0);
    }}
}}

@keyframes spin {{
    from {{
        transform: rotate(0deg);
    }}
    to {{
        transform: rotate(360deg);
    }}
}}

@media (prefers-reduced-motion: reduce) {{
    * {{
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
    }}
}}

@media (max-width: 1000px) {{
    .sidebar {{
        position: relative;
        width: 100%;
        height: auto;
    }}

    .main {{
        margin-left: 0;
        padding: 20px;
    }}

    .page-header {{
        flex-direction: column;
        align-items: flex-start;
    }}

    .progress-card {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 900px) {{
    .results-table thead {{
        display: none;
    }}

    .results-table,
    .results-table tbody,
    .results-table tr,
    .results-table td {{
        display: block;
        width: 100%;
    }}

    .results-table tr {{
        background: rgba(8, 17, 32, 0.65);
        margin-bottom: 16px;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.12);
    }}

    .results-table td {{
        border-bottom: 1px solid rgba(148, 163, 184, 0.10);
    }}

    .results-table td:last-child {{
        border-bottom: none;
    }}
}}
</style>

<script>
function showSection(id) {{
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("staff").style.display = "none";
    document.getElementById("it").style.display = "none";
    document.getElementById(id).style.display = "block";

    if (id === "dashboard") {{
        animateCounters();
        animateAllProgressRings();
    }}
}}

function animateValue(element, start, end, duration, suffix = "", decimals = 0) {{
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduceMotion) {{
        element.textContent = end.toFixed(decimals) + suffix;
        return;
    }}

    let startTimestamp = null;

    function step(timestamp) {{
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * eased;
        element.textContent = current.toFixed(decimals) + suffix;

        if (progress < 1) {{
            window.requestAnimationFrame(step);
        }}
    }}

    window.requestAnimationFrame(step);
}}

function animateCounters(scope = document) {{
    const counters = scope.querySelectorAll('[data-counter]');
    counters.forEach(counter => {{
        if (counter.dataset.animated === "true") return;

        const value = parseFloat(counter.dataset.value || "0");
        const suffix = counter.dataset.suffix || "";
        const decimals = parseInt(counter.dataset.decimals || "0", 10);
        animateValue(counter, 0, value, 1200, suffix, decimals);
        counter.dataset.animated = "true";
    }});
}}

function animateRingByElement(ring) {{
    if (!ring || ring.dataset.animated === "true") return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const radius = parseFloat(ring.dataset.radius || "42");
    const circumference = 2 * Math.PI * radius;
    const percent = parseFloat(ring.dataset.percent || "0");
    const offset = circumference - (percent / 100) * circumference;
    const labelId = ring.dataset.label;
    const label = labelId ? document.getElementById(labelId) : null;

    ring.style.strokeDasharray = circumference.toFixed(2);

    if (reduceMotion) {{
        ring.style.strokeDashoffset = offset.toFixed(2);
        if (label) label.textContent = percent.toFixed(0) + "%";
        ring.dataset.animated = "true";
        return;
    }}

    ring.style.strokeDashoffset = circumference.toFixed(2);
    requestAnimationFrame(() => {{
        ring.style.strokeDashoffset = offset.toFixed(2);
    }});

    if (label) {{
        animateValue(label, 0, percent, 1200, "%", 0);
    }}

    ring.dataset.animated = "true";
}}

function animateAllProgressRings(scope = document) {{
    const rings = scope.querySelectorAll('[data-progress-ring="true"]');
    rings.forEach(ring => animateRingByElement(ring));
}}

function hideLoader() {{
    const loader = document.getElementById('loading-screen');
    if (!loader) return;
    loader.classList.add('hidden');
}}

window.addEventListener('load', () => {{
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const delay = reduceMotion ? 250 : 1200;

    animateCounters();
    animateAllProgressRings();

    setTimeout(() => {{
        hideLoader();
    }}, delay);
}});

function buildResultRingCard(title, value, percentValue, labelId, ringId) {{
    return `
        <div class="card fade-in">
            <h3>${{title}}</h3>
            <div class="progress-card">
                <div class="progress-ring-wrap">
                    <svg class="progress-ring small" viewBox="0 0 100 100" aria-hidden="true">
                        <defs>
                            <linearGradient id="${{ringId}}-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#67e8f9" />
                                <stop offset="100%" stop-color="#3b82f6" />
                            </linearGradient>
                        </defs>
                        <circle class="ring-bg" cx="50" cy="50" r="42"></circle>
                        <circle
                            id="${{ringId}}"
                            class="ring-progress"
                            cx="50"
                            cy="50"
                            r="42"
                            data-progress-ring="true"
                            data-percent="${{percentValue}}"
                            data-radius="42"
                            data-label="${{labelId}}"
                            style="stroke:url(#${{ringId}}-gradient);stroke-dasharray:263.89;stroke-dashoffset:263.89;"
                        ></circle>
                    </svg>
                    <div id="${{labelId}}" class="progress-value small">0%</div>
                </div>

                <div class="metric-block">
                    <p class="score">${{value}}</p>
                    <span class="metric-caption">Visual score</span>
                </div>
            </div>
        </div>
    `;
}}

function submitStaffAudit() {{
    let score = 0;
    let total = 0;
    let recommendations = [];

    let answers = document.querySelectorAll(".staff-question");

    answers.forEach((q) => {{
        total += 1;

        if (q.selectedIndex === 0) {{
            score += 2;
        }} else if (q.selectedIndex === 1) {{
            score += 1;
        }} else {{
            if (q.dataset.issue) {{
                recommendations.push(q.dataset.issue);
            }}
        }}
    }});

    let percent = (score / (total * 2)) * 100;
    let risk = "";

    if (percent >= 80) {{
        risk = "LOW RISK";
    }} else if (percent >= 50) {{
        risk = "MEDIUM RISK";
    }} else {{
        risk = "HIGH RISK";
    }}

    document.getElementById("staff-result").innerHTML = `
    <div class="section fade-in">
        <h2>📋 Staff Security Audit Report</h2>
        <p class="section-subtitle">This summary reflects workforce cyber hygiene, account security behavior, and patient-data handling practices.</p>

        <div class="card-container">
            ${{buildResultRingCard("Security Awareness Score", `${{percent.toFixed(2)}}%`, percent.toFixed(2), "staff-ring-label", "staff-ring")}}

            <div class="card fade-in">
                <h3>Risk Level</h3>
                <div class="metric-row">
                    <div class="metric-block">
                        <p class="score ${{risk === 'LOW RISK' ? 'low' : risk === 'MEDIUM RISK' ? 'medium' : 'high'}}">${{risk}}</p>
                        <span class="metric-caption">Risk outcome</span>
                    </div>
                </div>
            </div>
        </div>

        <h3 style="margin-bottom:14px;color:#f8fbff;">🔍 Recommendations</h3>

        ${{
            recommendations.length > 0
            ? recommendations.map(r => `<div class="alert">${{r}}</div>`).join("")
            : `<div class="alert success">
                Excellent security practices detected.
               </div>`
        }}
    </div>
    `;

    const scope = document.getElementById("staff-result");
    animateAllProgressRings(scope);
}}

function submitITAudit() {{
    let score = 0;
    let total = 0;
    let recommendations = [];

    let answers = document.querySelectorAll(".it-question");

    answers.forEach((q) => {{
        total += 1;

        if (q.value == "Implemented") {{
            score += 2;
        }} else if (q.value == "Partial") {{
            score += 1;
        }} else {{
            if (q.dataset.issue) {{
                recommendations.push(q.dataset.issue);
            }}
        }}
    }});

    let percent = (score / (total * 2)) * 100;
    let risk = "";

    if (percent >= 80) {{
        risk = "LOW RISK";
    }} else if (percent >= 50) {{
        risk = "MEDIUM RISK";
    }} else {{
        risk = "HIGH RISK";
    }}

    document.getElementById("it-result").innerHTML = `
    <div class="section fade-in">
        <h2>💻 IT Security Audit Report</h2>
        <p class="section-subtitle">This report reflects security control maturity across infrastructure, monitoring, encryption, and privileged access management.</p>

        <div class="card-container">
            ${{buildResultRingCard("IT Security Readiness", `${{percent.toFixed(2)}}%`, percent.toFixed(2), "it-ring-label", "it-ring")}}

            <div class="card fade-in">
                <h3>Risk Level</h3>
                <div class="metric-row">
                    <div class="metric-block">
                        <p class="score ${{risk === 'LOW RISK' ? 'low' : risk === 'MEDIUM RISK' ? 'medium' : 'high'}}">${{risk}}</p>
                        <span class="metric-caption">Infrastructure risk</span>
                    </div>
                </div>
            </div>
        </div>

        <h3 style="margin-bottom:14px;color:#f8fbff;">🛡️ Security Recommendations</h3>

        ${{
            recommendations.length > 0
            ? recommendations.map(r => `<div class="alert">${{r}}</div>`).join("")
            : `<div class="alert success">
                Infrastructure security controls appear properly implemented.
               </div>`
        }}
    </div>
    `;

    const scope = document.getElementById("it-result");
    animateAllProgressRings(scope);
}}
</script>
</head>

<body>
<div id="loading-screen" class="loading-screen" aria-live="polite">
    <div class="loader-ring"></div>
    <div class="loader-title">HC DASHBOARD</div>
    <div class="loader-subtitle">Loading security intelligence...</div>
</div>

<div class="sidebar">
    <div class="brand">
        <h2>HC DASHBOARD</h2>
        <p>HealthCare security monitoring for compliance posture, workforce awareness, and infrastructure readiness.</p>
    </div>

    <button onclick="showSection('dashboard')">📊 Compliance Dashboard</button>
    <button onclick="showSection('staff')">👨‍⚕️ Healthcare Staff Audit</button>
    <button onclick="showSection('it')">💻 IT Security Audit</button>
</div>

<div class="main">

<div id="dashboard">
    <div class="page-header">
        <div class="page-title">
            <h1>Healthcare Security Command Center</h1>
            <p>Real-time compliance visibility, workforce security posture, and infrastructure risk monitoring for healthcare environments.</p>
        </div>
        <div class="status-pill">● Secure Monitoring Active</div>
    </div>

    <div class="card-container">
        <div class="card">
            <h3>Compliance Score</h3>
            <div class="progress-card">
                <div class="progress-ring-wrap">
                    <svg class="progress-ring" viewBox="0 0 100 100" aria-hidden="true">
                        <defs>
                            <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#67e8f9" />
                                <stop offset="100%" stop-color="#3b82f6" />
                            </linearGradient>
                        </defs>
                        <circle class="ring-bg" cx="50" cy="50" r="42"></circle>
                        <circle
                            id="compliance-ring"
                            class="ring-progress"
                            cx="50"
                            cy="50"
                            r="42"
                            data-progress-ring="true"
                            data-percent="{percent:.2f}"
                            data-radius="42"
                            data-label="ring-label"
                        ></circle>
                    </svg>
                    <div id="ring-label" class="progress-value">0%</div>
                </div>

                <div class="metric-block">
                    <p class="score" data-counter="true" data-value="{percent:.2f}" data-suffix="%" data-decimals="2">0.00%</p>
                    <span class="metric-caption">Overall posture</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Risk Level</h3>
            <div class="metric-row">
                <div class="metric-block">
                    <p class="score {'low' if overall == 'LOW RISK' else 'medium' if overall == 'MEDIUM RISK' else 'high'}">{overall}</p>
                    <span class="metric-caption">Assessment result</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Passed Controls</h3>
            <div class="metric-row">
                <div class="metric-block">
                    <p class="score" data-counter="true" data-value="{passed}" data-suffix="" data-decimals="0">0</p>
                    <span class="metric-caption">Compliant checks</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Failed Controls</h3>
            <div class="metric-row">
                <div class="metric-block">
                    <p class="score" data-counter="true" data-value="{failed}" data-suffix="" data-decimals="0">0</p>
                    <span class="metric-caption">Risk exposures</span>
                </div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>🚨 Security Alerts</h2>
        <p class="section-subtitle">Automated detection highlights suspicious activity and authentication anomalies.</p>
"""

for a in alerts:
    html += f'<div class="alert">{a}</div>\n'

if not alerts:
    html += '<div class="alert success">No active security alerts detected.</div>\n'

html += """
    </div>

    <div class="section">
        <h2>📋 Compliance Results</h2>
        <p class="section-subtitle">
            Review each control, its compliance status, associated risk level, supporting evidence, and the recommended action.
        </p>

        <table class="results-table">
            <thead>
                <tr>
                    <th>Security Control</th>
                    <th>Status</th>
                    <th>Risk</th>
                    <th>Evidence</th>
                    <th>Recommended Action</th>
                </tr>
            </thead>
            <tbody>
"""

for r in results:
    if r["status"] == "COMPLIANT":
        status_badge = '<span class="badge badge-success">Compliant</span>'
    elif r["status"] == "NON-COMPLIANT":
        status_badge = '<span class="badge badge-danger">Non-Compliant</span>'
    else:
        status_badge = '<span class="badge badge-warning">Insufficient Data</span>'

    risk_class = (
        "risk-high" if r["risk"] == "High"
        else "risk-medium" if r["risk"] == "Medium"
        else "risk-low"
    )

    html += f"""
                <tr>
                    <td>
                        <div class="control-title">{r['desc']}</div>
                        <div class="control-note">Security requirement check</div>
                    </td>
                    <td>{status_badge}</td>
                    <td><span class="{risk_class}">{r['risk']}</span></td>
                    <td><div class="evidence-box">{r['evidence']}</div></td>
                    <td><div class="remediation-box">{r['remediation']}</div></td>
                </tr>
"""

html += """
            </tbody>
        </table>
    </div>
</div>

<div id="staff" class="hidden">
    <div class="page-header">
        <div class="page-title">
            <h1>Healthcare Staff Security Audit</h1>
            <p>Assess workforce security habits, awareness levels, and patient-data handling behavior.</p>
        </div>
        <div class="status-pill">● Staff Review Mode</div>
    </div>

    <div class="section">
        <h2>🔐 Authentication & Password Security</h2>

        <label>When do you change your password?</label>
        <select class="staff-question" data-issue="Passwords should be changed immediately if compromise is suspected, and staff should follow the organization’s password policy.">
            <option>When required by policy or if compromise is suspected</option>
            <option>Only when prompted by the system</option>
            <option>I rarely or never change it</option>
        </select>

        <label>Do you ever share your password with coworkers?</label>
        <select class="staff-question" data-issue="Password sharing increases insider threat and unauthorized access risks.">
            <option>Never</option>
            <option>Only in urgent situations</option>
            <option>Yes</option>
        </select>

        <label>Do you use MFA for healthcare systems?</label>
        <select class="staff-question" data-issue="MFA should be enabled to protect patient records and privileged access.">
            <option>Yes, always</option>
            <option>Only for some systems</option>
            <option>No</option>
        </select>
    </div>

    <div class="section">
        <h2>📧 Email & Phishing Awareness</h2>

        <label>How confident are you in identifying phishing emails?</label>
        <select class="staff-question" data-issue="Additional phishing awareness training is recommended.">
            <option>Very confident and I verify suspicious messages</option>
            <option>Somewhat confident</option>
            <option>Not confident</option>
        </select>

        <label>Have you completed cybersecurity awareness training recently?</label>
        <select class="staff-question" data-issue="Regular cybersecurity awareness training should be mandatory.">
            <option>Yes, within the last 12 months</option>
            <option>More than 12 months ago</option>
            <option>No</option>
        </select>

        <label>Do you report suspicious emails immediately?</label>
        <select class="staff-question" data-issue="Suspicious emails should be reported immediately to IT or Security teams.">
            <option>Yes, always</option>
            <option>Sometimes</option>
            <option>No</option>
        </select>
    </div>

    <div class="section">
        <h2>🏥 Patient Data Handling</h2>

        <label>Do you leave workstations unlocked when unattended?</label>
        <select class="staff-question" data-issue="Unlocked workstations may expose sensitive healthcare information.">
            <option>Never</option>
            <option>Sometimes</option>
            <option>Yes, often</option>
        </select>

        <label>Do you access patient records only when required for your job?</label>
        <select class="staff-question" data-issue="Access to patient records should follow least privilege principles.">
            <option>Yes, always</option>
            <option>Sometimes</option>
            <option>No</option>
        </select>

        <label>Do you use personal USB devices on work systems?</label>
        <select class="staff-question" data-issue="Unauthorized USB devices may introduce malware into healthcare systems.">
            <option>Never</option>
            <option>Only with approval</option>
            <option>Yes</option>
        </select>

        <button class="submit-btn" onclick="submitStaffAudit()">
            Generate Staff Audit Report
        </button>
    </div>

    <div id="staff-result"></div>
</div>

<div id="it" class="hidden">
    <div class="page-header">
        <div class="page-title">
            <h1>IT Security Infrastructure Audit</h1>
            <p>Review technical safeguards, monitoring maturity, and infrastructure resilience controls.</p>
        </div>
        <div class="status-pill">● IT Audit Mode</div>
    </div>

    <div class="section">
        <h2>🔐 Access Control & Authentication</h2>

        <label>Is MFA enabled for privileged accounts?</label>
        <select class="it-question" data-issue="Privileged accounts should always use MFA protection.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <label>Is Role-Based Access Control implemented?</label>
        <select class="it-question" data-issue="RBAC helps reduce excessive privilege exposure.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <label>Are inactive accounts automatically disabled?</label>
        <select class="it-question" data-issue="Inactive accounts should be disabled to reduce unauthorized access risks.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>
    </div>

    <div class="section">
        <h2>📊 Logging & Monitoring</h2>

        <label>Is audit logging enabled?</label>
        <select class="it-question" data-issue="Audit logs are required for healthcare compliance investigations.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <label>Are logs reviewed regularly?</label>
        <select class="it-question" data-issue="Regular log review improves threat detection and incident response.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <label>Is a SIEM platform deployed?</label>
        <select class="it-question" data-issue="SIEM deployment improves centralized monitoring and alerting.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>
    </div>

    <div class="section">
        <h2>🛡️ Infrastructure Security</h2>

        <label>Are backups encrypted?</label>
        <select class="it-question" data-issue="Healthcare backups should always be encrypted to protect PHI.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <label>Is TLS/HTTPS enforced?</label>
        <select class="it-question" data-issue="Encrypted communication channels should be enforced organization-wide.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <label>Are vulnerability scans performed monthly?</label>
        <select class="it-question" data-issue="Regular vulnerability scanning is critical for proactive security management.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <label>Is endpoint protection installed?</label>
        <select class="it-question" data-issue="Endpoint protection helps reduce malware and ransomware risks.">
            <option>Implemented</option>
            <option>Partial</option>
            <option>Not Implemented</option>
        </select>

        <button class="submit-btn" onclick="submitITAudit()">
            Generate IT Audit Report
        </button>
    </div>

    <div id="it-result"></div>
</div>

</div>
</body>
</html>
"""


# =========================================================
# SAVE REPORT
# =========================================================

REPORT_FILE.write_text(html, encoding="utf-8")


# =========================================================
# OPEN REPORT
# =========================================================

webbrowser.open_new_tab(REPORT_FILE.resolve().as_uri())