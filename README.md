# Healthcare Compliance Dashboard

A Streamlit-based dashboard built as a sub-repo for the main `checker` project. It turns the original compliance checker into a more usable web app with employee login, role-based access, audit scoring, and a cleaner interface for reviewing healthcare security posture.

![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/streamlit-dashboard-red?style=flat-square&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/status-in%20progress-green?style=flat-square)

## Why this exists

The original `checker.py` works well for core compliance logic, but it feels more like a script than a full application. This repo exists to make that logic easier to interact with by giving it a proper UI, login flow, role-based pages, and more readable audit output.

The goal was not to replace the main checker, but to build a cleaner frontend-style layer around it.

## What this app does

This app lets different employees log in and see the parts of the system that matter to them.

It currently includes:
- A login screen for employees based on role
- An admin dashboard with compliance summaries and alerts
- An IT security audit page with technical questions and scoring
- A staff audit page focused on security awareness and PHI handling
- A compliance review page for findings, evidence, and remediation
- Shared scoring logic for overall security posture and risk level

## Built from the main checker

This repository is meant to be a sub-repo for the main checker project.

The main checker provides the base ideas:
- control checking
- audit logic
- scoring concepts
- risk evaluation

This Streamlit version builds on that by adding:
- a web interface
- better layout and navigation
- role-based access
- more user-friendly audit flows
- improved presentation of findings


### Main dashboard
![Dashboard preview](https://github.com/HealthcareCompilanceLab/helathcare-compilence-app/blob/main/login%20page.png)

### Audit pages
<p align="center">
  <img src="https://github.com/HealthcareCompilanceLab/helathcare-compilence-app/blob/main/it%20security.png" alt="IT audit preview" width="48%" />
  <img src="https://github.com/HealthcareCompilanceLab/helathcare-compilence-app/blob/main/staff%20audit.png" alt="Staff audit preview" width="48%" />
</p>

## Roles in the app

| Role | What they can access |
|---|---|
| Admin | Dashboard, compliance results, findings, alerts, and overall posture |
| IT Security | Technical audit questions, infrastructure findings, and system posture |
| Healthcare Staff | Staff-focused audit questions and awareness review |
| Compliance Officer | Compliance findings, evidence, and remediation review |

## Pages

### Admin Dashboard
The admin view is the main summary page. It shows compliance score, risk level, passed and failed controls, active alerts, and current findings.

### IT Security Audit
The IT page is focused on technical controls like MFA, RBAC, audit logging, SIEM, encrypted backups, TLS, vulnerability scanning, and endpoint protection.

### Staff Audit
The staff page is focused on user behavior and security awareness. It covers password habits, phishing awareness, patient data handling, workstation safety, and incident reporting.

### Compliance Officer Review
This page is meant for reviewing control-level outcomes in a cleaner format, including evidence and remediation details.

## Project structure

```text
healthcare-compliance-dashboard/
├── app.py
├── auth.py
├── utils.py
├── employees.json
├── control_bank.json
├── system_data.json
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── pages/
    ├── 1_Admin_Dashboard.py
    ├── 2_IT_Security.py
    ├── 3_Staff_Audit.py
    └── 4_Compliance_Officer.py
```

## Running the app

### 1. Clone the repo
```bash
git clone (https://github.com/HealthcareCompilanceLab/helathcare-compilence-app)
cd healthcare-compliance-dashboard
```

### 2. Install requirements
```bash
pip install -r requirements.txt
```

### 3. Start Streamlit
```bash
python -m streamlit run app.py
```

## Example accounts

These are example accounts used for testing:

- `EMP001 / admin123` — Admin
- `EMP002 / itsecure123` — IT Security
- `EMP003 / staff123` — Healthcare Staff
- `EMP004 / compliance123` — Compliance Officer

## Files and data

- `employees.json` stores employee login details and access roles
- `control_bank.json` stores the compliance controls
- `system_data.json` stores the system/security values used for scoring
- `auth.py` handles login, logout, and access checks
- `utils.py` contains shared UI helpers and compliance functions

## Current focus

Right now the app is mainly focused on making the main checker easier to demo, easier to navigate, and easier to review by role.

It is especially useful for:
- project demos
- coursework or portfolio presentation
- internal walkthroughs
- showing how script logic can be turned into a real dashboard

## Future improvements

A few things that could be added next:
- report export
- charts and trend tracking
- stronger admin controls
- better data persistence
- real screenshots instead of placeholders
- tighter integration with the main checker repo

## Notes

This repo is best thought of as the UI/dashboard companion to the main checker project. The main logic comes from the checker idea, while this repo focuses on presentation, usability, and role-based interaction.
