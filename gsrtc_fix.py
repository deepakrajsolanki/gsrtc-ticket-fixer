import asyncio
import sys
import re
from playwright.async_api import async_playwright

async def fix_gsrtc_ticket(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 960, "height": 1400})

        print(f"Opening: {url}")
        await page.goto(url, wait_until="networkidle")

        await page.evaluate("""
            () => {
                // 1. Fix outer container only
                const content = document.getElementById('content');
                if (content) {
                    content.style.width    = '100%';
                    content.style.maxWidth = 'none';
                    content.style.overflow = 'visible';
                }
                document.body.style.width    = '100%';
                document.body.style.margin   = '0';
                document.body.style.padding  = '0';
                document.body.style.overflow = 'visible';
                document.documentElement.style.overflow = 'visible';
                document.documentElement.style.width    = '100%';

                // 2. Remove fixed px width ONLY on non-table elements
                document.querySelectorAll('[style]').forEach(el => {
                    if (['TABLE','TD','TR','TH'].includes(el.tagName)) return;
                    const st = el.getAttribute('style') || '';
                    if (st.match(/width\s*:\s*\d+px/i)) {
                        el.setAttribute('style',
                            st.replace(/width\s*:\s*\d+px/gi, 'width:100%')
                              .replace(/overflow\s*:\s*hidden/gi, 'overflow:visible')
                        );
                    }
                });

                // 3. ONLY fix the Boarding/Arrival header row cells to be 50/50
                //    Find the specific TR that has BOTH "Boarding From" and "Arrival"
                document.querySelectorAll('tr').forEach(row => {
                    const cells = row.querySelectorAll('td');
                    const text  = row.innerText || '';
                    if (text.includes('Boarding From') && text.includes('Arrival') && cells.length === 2) {
                        cells[0].style.width = '50%';
                        cells[1].style.width = '50%';
                    }
                });
            }
        """)

        try:
            body_text = await page.inner_text("body")
            match = re.search(r'[A-Z]\d{9}', body_text)
            pnr = match.group(0) if match else "GSRTC_Ticket"
        except:
            pnr = "GSRTC_Ticket"

        output_file = f"{pnr}_FIXED.pdf"

        await page.pdf(
            path=output_file,
            format="A4",
            landscape=False,
            margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"},
            print_background=True,
            scale=0.85
        )

        await browser.close()
        print(f"✅ PDF saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        url = input("Paste GSRTC ticket URL: ").strip()
    else:
        url = sys.argv[1]

    asyncio.run(fix_gsrtc_ticket(url))