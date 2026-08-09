import streamlit as st
import asyncio
import subprocess
import sys
import re

@st.cache_resource
def install_playwright_browsers():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    except Exception as e:
        print(f"Playwright browser install warning: {e}")

install_playwright_browsers()

from playwright.async_api import async_playwright

st.set_page_config(
    page_title="GSRTC Ticket Fixer", 
    page_icon="🎫", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit Embed toolbar, footer, headers completely
st.markdown("""
<style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .stAppToolbar {display: none !important;}
    .viewerBadge_container__1QS1n {display: none !important;}
    .viewerBadge_link__1S137 {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    div[class*="styles_viewerBadge"] {display: none !important;}
    div[data-testid="stEmbedFooter"] {display: none !important;}
    footer[data-testid="stFooter"] {display: none !important;}
    footer:after {display: none !important;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 750px !important;
    }
    .developer-credit {
        text-align: center;
        font-size: 13px;
        color: #888888;
        margin-top: 25px;
        border-top: 1px solid #333333;
        padding-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎫 GSRTC Ticket PDF Fixer")
st.write("Fix right-side cropping and download clean PDF GSRTC e-tickets.")

url = st.text_input("Paste GSRTC Ticket URL:", placeholder="https://www.gsrtc.in/OPRSOnline/viewTicket.do?TKTN=...")

async def fix_gsrtc_ticket(ticket_url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 960, "height": 1400})
        await page.goto(ticket_url, wait_until="networkidle")

        await page.evaluate("""
            () => {
                const content = document.getElementById("content");
                if (content) {
                    content.style.width    = "100%";
                    content.style.maxWidth = "none";
                    content.style.overflow = "visible";
                }
                document.body.style.width    = "100%";
                document.body.style.margin   = "0";
                document.body.style.padding  = "0";
                document.body.style.overflow = "visible";
                document.documentElement.style.overflow = "visible";
                document.documentElement.style.width    = "100%";

                document.querySelectorAll("[style]").forEach(el => {
                    if (["TABLE","TD","TR","TH"].includes(el.tagName)) return;
                    const st = el.getAttribute("style") || "";
                    if (st.match(/width\s*:\s*\d+px/i)) {
                        el.setAttribute("style",
                            st.replace(/width\s*:\s*\d+px/gi, "width:100%")
                              .replace(/overflow\s*:\s*hidden/gi, "overflow:visible")
                        );
                    }
                });

                document.querySelectorAll("tr").forEach(row => {
                    const cells = row.querySelectorAll("td");
                    const text  = row.innerText || "";
                    if (text.includes("Boarding From") && text.includes("Arrival") && cells.length === 2) {
                        cells[0].style.width = "50%";
                        cells[1].style.width = "50%";
                    }
                });
            }
        """)

        try:
            body_text = await page.inner_text("body")
            match = re.search(r"[A-Z]\d{9}", body_text)
            pnr = match.group(0) if match else "GSRTC_Ticket"
        except:
            pnr = "GSRTC_Ticket"

        pdf_bytes = await page.pdf(
            format="A4",
            landscape=False,
            margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"},
            print_background=True,
            scale=0.85
        )
        await browser.close()
        return pnr, pdf_bytes

if st.button("Generate & Fix PDF", type="primary"):
    if not url or "gsrtc.in" not in url:
        st.error("Please enter a valid GSRTC ticket URL.")
    else:
        with st.spinner("Running Python Playwright engine..."):
            try:
                pnr, pdf_data = asyncio.run(fix_gsrtc_ticket(url))
                st.success(f"Ticket processed successfully! PNR: {pnr}")
                st.download_button(
                    label="📥 Download Fixed PDF",
                    data=pdf_data,
                    file_name=f"{pnr}_FIXED.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error processing ticket: {str(e)}")

st.markdown("""
<div class="developer-credit">
    Developed by <strong>Solaank Technologies</strong>
</div>
""", unsafe_allow_html=True)
