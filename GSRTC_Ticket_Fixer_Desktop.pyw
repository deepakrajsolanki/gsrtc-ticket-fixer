import asyncio
import os
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Playwright async engine
from playwright.async_api import async_playwright

class GSRTCFixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GSRTC Ticket Fixer — Windows Desktop App")
        self.root.geometry("640x520")
        self.root.minsize(580, 480)
        
        # Configure fonts and modern theme colors
        self.bg_color = "#f4f6f9"
        self.card_bg = "#ffffff"
        self.primary_color = "#1e88e5"
        self.accent_color = "#1565c0"
        self.success_color = "#2e7d32"
        self.text_dark = "#212121"
        self.text_muted = "#666666"

        self.root.configure(bg=self.bg_color)
        
        # Default destination: User's Downloads folder
        downloads_path = str(Path.home() / "Downloads")
        self.save_dir_var = tk.StringVar(value=downloads_path)
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready. Paste your GSRTC ticket URL below.")
        self.last_generated_pdf = None

        self.setup_ui()
        self.check_clipboard_for_ticket()

    def setup_ui(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg="#0d47a1", padx=20, pady=16)
        header_frame.pack(fill="x")

        lbl_title = tk.Label(
            header_frame, 
            text="🚍 GSRTC Ticket PDF Fixer", 
            font=("Segoe UI", 16, "bold"), 
            fg="#ffffff", 
            bg="#0d47a1"
        )
        lbl_title.pack(anchor="w")

        lbl_subtitle = tk.Label(
            header_frame, 
            text="Fix right-side clipping, fix table layout, and export clean A4 PDFs", 
            font=("Segoe UI", 9), 
            fg="#e3f2fd", 
            bg="#0d47a1"
        )
        lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # Main Card Container
        main_card = tk.Frame(self.root, bg=self.card_bg, padx=20, pady=20, bd=1, relief="solid")
        main_card.pack(fill="both", expand=True, padx=20, pady=16)

        # 1. URL Input Section
        lbl_url = tk.Label(
            main_card, 
            text="GSRTC Ticket URL:", 
            font=("Segoe UI", 10, "bold"), 
            fg=self.text_dark, 
            bg=self.card_bg
        )
        lbl_url.pack(anchor="w")

        url_input_frame = tk.Frame(main_card, bg=self.card_bg)
        url_input_frame.pack(fill="x", pady=(6, 12))

        self.entry_url = ttk.Entry(url_input_frame, textvariable=self.url_var, font=("Segoe UI", 10))
        self.entry_url.pack(side="left", fill="x", expand=True, ipady=4)

        btn_paste = tk.Button(
            url_input_frame, 
            text="📋 Paste", 
            command=self.paste_from_clipboard,
            font=("Segoe UI", 9),
            bg="#e0e0e0", 
            relief="flat", 
            padx=10, 
            cursor="hand2"
        )
        btn_paste.pack(side="left", padx=(8, 0))

        # 2. Output Folder Section
        lbl_folder = tk.Label(
            main_card, 
            text="Save Destination:", 
            font=("Segoe UI", 10, "bold"), 
            fg=self.text_dark, 
            bg=self.card_bg
        )
        lbl_folder.pack(anchor="w")

        folder_frame = tk.Frame(main_card, bg=self.card_bg)
        folder_frame.pack(fill="x", pady=(6, 16))

        self.entry_folder = ttk.Entry(folder_frame, textvariable=self.save_dir_var, font=("Segoe UI", 9))
        self.entry_folder.pack(side="left", fill="x", expand=True, ipady=3)

        btn_browse = tk.Button(
            folder_frame, 
            text="📁 Browse...", 
            command=self.browse_folder,
            font=("Segoe UI", 9),
            bg="#e0e0e0", 
            relief="flat", 
            padx=10, 
            cursor="hand2"
        )
        btn_browse.pack(side="left", padx=(8, 0))

        # 3. Action Buttons Section
        self.btn_generate = tk.Button(
            main_card, 
            text="⚡ Generate & Fix Ticket PDF", 
            command=self.start_processing,
            font=("Segoe UI", 11, "bold"),
            bg=self.primary_color, 
            fg="#ffffff", 
            activebackground=self.accent_color,
            activeforeground="#ffffff",
            relief="flat", 
            pady=8,
            cursor="hand2"
        )
        self.btn_generate.pack(fill="x", pady=(4, 12))

        # Progress bar (indeterminate)
        self.progress_bar = ttk.Progressbar(main_card, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 10))

        # Status text
        self.lbl_status = tk.Label(
            main_card, 
            textvariable=self.status_var, 
            font=("Segoe UI", 9, "italic"), 
            fg=self.text_muted, 
            bg=self.card_bg,
            wraplength=550,
            justify="left"
        )
        self.lbl_status.pack(anchor="w")

        # 4. Result Action Buttons (Hidden until PDF generated)
        self.result_frame = tk.Frame(main_card, bg=self.card_bg)
        self.result_frame.pack(fill="x", pady=(12, 0))

        self.btn_open_pdf = tk.Button(
            self.result_frame,
            text="📄 Open Fixed PDF",
            command=self.open_generated_pdf,
            font=("Segoe UI", 9, "bold"),
            bg="#2e7d32",
            fg="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_open_pdf.pack(side="left", padx=(0, 8))

        self.btn_open_folder = tk.Button(
            self.result_frame,
            text="📂 Open Containing Folder",
            command=self.open_output_folder,
            font=("Segoe UI", 9),
            bg="#455a64",
            fg="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_open_folder.pack(side="left")
        self.result_frame.pack_forget()

        # Footer Credit
        footer_lbl = tk.Label(
            self.root, 
            text="Developed by Solaank Technologies • Powered by Playwright Chromium Engine", 
            font=("Segoe UI", 8), 
            fg="#9e9e9e", 
            bg=self.bg_color,
            pady=8
        )
        footer_lbl.pack(side="bottom")

    def check_clipboard_for_ticket(self):
        try:
            cb_text = self.root.clipboard_get().strip()
            if "gsrtc.in" in cb_text and ("http://" in cb_text or "https://" in cb_text):
                self.url_var.set(cb_text)
                self.status_var.set("Detected GSRTC ticket link in clipboard! Click 'Generate & Fix Ticket PDF'.")
        except Exception:
            pass

    def paste_from_clipboard(self):
        try:
            text = self.root.clipboard_get().strip()
            self.url_var.set(text)
            self.status_var.set("URL pasted from clipboard.")
        except Exception:
            messagebox.showwarning("Clipboard", "Clipboard is empty or does not contain plain text.")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_dir_var.get())
        if folder:
            self.save_dir_var.set(folder)

    def set_ui_busy(self, is_busy: bool, message: str = ""):
        if message:
            self.status_var.set(message)
        if is_busy:
            self.btn_generate.config(state="disabled", bg="#90caf9")
            self.progress_bar.start(10)
            self.result_frame.pack_forget()
        else:
            self.btn_generate.config(state="normal", bg=self.primary_color)
            self.progress_bar.stop()

    def start_processing(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please paste or enter a GSRTC ticket URL.")
            return

        if "gsrtc.in" not in url or not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showerror("Invalid URL", "Please provide a valid URL from gsrtc.in.")
            return

        out_dir = self.save_dir_var.get().strip()
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Directory Error", f"Cannot create directory:\n{e}")
                return

        self.set_ui_busy(True, "Starting background Playwright engine...")
        
        # Run in separate thread to prevent freezing the UI
        thread = threading.Thread(target=self.run_playwright_job, args=(url, out_dir), daemon=True)
        thread.start()

    def run_playwright_job(self, url: str, out_dir: str):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result_path = loop.run_until_complete(self.async_fix_ticket(url, out_dir))
            loop.close()

            self.root.after(0, self.on_job_success, result_path)
        except Exception as e:
            self.root.after(0, self.on_job_error, str(e))

    async def async_fix_ticket(self, url: str, out_dir: str):
        self.root.after(0, lambda: self.status_var.set("Connecting to GSRTC and loading ticket page..."))

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 960, "height": 1400})

            await page.goto(url, wait_until="networkidle", timeout=45000)

            self.root.after(0, lambda: self.status_var.set("Applying layout and responsive table styling..."))

            # Apply DOM and CSS fixes
            await page.evaluate(r"""
                () => {
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
            except Exception:
                pnr = "GSRTC_Ticket"

            self.root.after(0, lambda: self.status_var.set(f"Generating clean A4 PDF for PNR: {pnr}..."))

            output_file = os.path.join(out_dir, f"{pnr}_FIXED.pdf")

            await page.pdf(
                path=output_file,
                format="A4",
                landscape=False,
                margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"},
                print_background=True,
                scale=0.85
            )

            await browser.close()
            return output_file

    def on_job_success(self, pdf_path: str):
        self.last_generated_pdf = pdf_path
        self.set_ui_busy(False, f"✔ Success! PDF saved: {os.path.basename(pdf_path)}")
        self.lbl_status.config(fg=self.success_color, font=("Segoe UI", 9, "bold"))
        self.result_frame.pack(fill="x", pady=(12, 0))

    def on_job_error(self, err_msg: str):
        self.set_ui_busy(False, f"❌ Failed: {err_msg}")
        self.lbl_status.config(fg="#c62828", font=("Segoe UI", 9, "bold"))
        messagebox.showerror("Generation Error", f"Failed to generate fixed ticket PDF:\n\n{err_msg}")

    def open_generated_pdf(self):
        if self.last_generated_pdf and os.path.exists(self.last_generated_pdf):
            try:
                os.startfile(self.last_generated_pdf)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open PDF file:\n{e}")

    def open_output_folder(self):
        if self.last_generated_pdf and os.path.exists(self.last_generated_pdf):
            folder = os.path.dirname(self.last_generated_pdf)
            subprocess.run(["explorer.exe", f"/select,{self.last_generated_pdf}"])
        else:
            folder = self.save_dir_var.get()
            if os.path.exists(folder):
                os.startfile(folder)

def main():
    root = tk.Tk()
    app = GSRTCFixerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
