# 🎫 GSRTC Ticket Fixer

A web application and CLI automation tool developed by **Solaank Technologies** to resolve right-side clipping bugs in GSRTC (Gujarat State Road Transport Corporation) e-tickets and generate clean A4 PDFs.

> [!NOTE]
> **AI Architecture & Development**: This entire project was created, designed, debugged, and deployed using **Google Antigravity** (AGY Pair Programming Agent).

---

## 🌐 Live Application & Cloud References
- **Official Live Application**: 👉 **[https://solaank.co.in/gsrtc-fixer/](https://solaank.co.in/gsrtc-fixer/)**
- **GitHub Repository**: **[https://github.com/deepakrajsolanki/gsrtc-ticket-fixer](https://github.com/deepakrajsolanki/gsrtc-ticket-fixer)**
- **Streamlit Engine Host**: **[https://share.streamlit.io](https://share.streamlit.io)** (gsrtc-ticket-fixer-kps5ps8dacgahycyzchhks.streamlit.app)

---

## 📜 Project Origins & Handover History

- **Origin State**: Started from an initial local Playwright script (gsrtc_fix.py) and an early HTML prototype that produced canvas layout clipping during browser rendering.
- **Antigravity Takeover**: Google Antigravity took over the codebase, diagnosed browser DOM canvas width rendering limitations, created the single-page A4 Playwright engine, built the Streamlit Cloud integration (pp.py), configured cloud Linux dependencies (packages.txt / equirements.txt), suppressed embedded UI toolbars, and integrated the custom domain wrapper for solaank.co.in/gsrtc-fixer/.
- **Last Worked On & Handed Over**: **August 9, 2026 at 19:15:00 IST**.

---

## 📂 Repository File Structure

| File | Purpose |
| :--- | :--- |
| **pp.py** | Main Streamlit application running the Playwright backend engine. |
| **gsrtc_fix.py** | Standalone Python Playwright script for local command-line execution. |
| **index.html** | Clean iframe wrapper page for hosting on custom domains (solaank.co.in/gsrtc-fixer/). |
| **equirements.txt** | Python dependencies (streamlit, playwright). |
| **packages.txt** | Linux system dependencies (chromium). |
| **Dockerfile** | Container setup for Docker-capable hosting environments. |

---

## 🛠️ Usage Instructions

### Method 1: Use Live Web Tool (Recommended)
Simply open **[https://solaank.co.in/gsrtc-fixer/](https://solaank.co.in/gsrtc-fixer/)**, paste your GSRTC ticket URL, and click **Generate & Fix PDF**.

### Method 2: Local Command Line Execution
To run the automated script directly on your computer:

`ash
# 1. Install dependencies
pip install playwright
python -m playwright install chromium

# 2. Run script with ticket URL
python gsrtc_fix.py " https://www.gsrtc.in/OPRSOnline/viewTicket.do?TKTN=...\
``n
---

## ⚠️ DOs and DONTs

### ✅ DOs:
- **DO** use full, active GSRTC ticket URLs (https://www.gsrtc.in/OPRSOnline/viewTicket.do?...).
- **DO** make sure Playwright Chromium is installed if running locally (python -m playwright install chromium).
- **DO** commit any changes to pp.py via GitHub to keep the cloud engine in sync.

### ❌ DONTs:
- **DONT** delete or overwrite equirements.txt or packages.txt—they ensure cloud servers pre-install Playwright dependencies.
- **DONT** remove the CSS overrides in pp.py or index.html unless you want Streamlit branding/toolbars to become visible again.
- **DONT** run gsrtc_fix.py on basic shared cPanel servers directly—shared hosting blocks Chromium root dependencies (use the Streamlit Cloud engine instead).

---

© Developed by **Solaank Technologies** using **Google Antigravity**
