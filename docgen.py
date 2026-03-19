import requests
import argparse
import os
from colorama import Fore, Style, init
import pdfkit
from tqdm import tqdm

# Initialize Colorama
init(autoreset=True)

API_URL = "http://127.0.0.1:8000/process"
WKHTML_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# ---------- LOG FUNCTIONS ----------
def log_process(msg): print(Fore.CYAN + "🔵 " + msg)
def log_info(msg): print(Fore.YELLOW + "🟡 " + msg)
def log_success(msg): print(Fore.GREEN + "🟢 " + msg)
def log_error(msg): print(Fore.RED + "🔴 " + msg)

# ---------- MARKDOWN ----------
def save_markdown(content, file):
    output = file + ".md"
    try:
        with open(output, "w", encoding="utf-8") as f:
            f.write(f"# Documentation for {file}\n\n```python\n{content}\n```")
        log_success(f"Saved {output}")
        return output
    except Exception as e:
        log_error(f"Markdown error: {e}")

# ---------- HTML (PDF-compatible) ----------
def save_html(content, file, style="google"):
    output = file + ".html"

    style_colors = {
        "google": "#4FC3F7",
        "numpy": "#FFCA28",
        "sphinx": "#8BC34A"
    }
    code_color = style_colors.get(style.lower(), "#4FC3F7")

    html_content = f"""
<html>
<head>
    <title>Generated Documentation</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #1e1e1e;
            color: white;
        }}
        h1 {{
            color: white;
        }}
        pre {{
            background: #2d2d2d;
            color: {code_color};
            padding: 20px;
            border-radius: 10px;
            font-family: Consolas, monospace;
            font-size: 14px;
            overflow-x: auto;
            line-height: 1.5;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <h1>Generated Documentation ({style.title()} Style)</h1>
    <pre>{content}</pre>
</body>
</html>
"""
    try:
        with open(output, "w", encoding="utf-8") as f:
            f.write(html_content)
        log_success(f"Saved {output}")
        return output
    except Exception as e:
        log_error(f"HTML error: {e}")

# ---------- PDF ----------
def save_pdf(html_file):
    pdf_file = html_file.replace(".html", ".pdf")
    try:
        config = pdfkit.configuration(wkhtmltopdf=WKHTML_PATH)
        pdfkit.from_file(html_file, pdf_file, configuration=config)
        log_success(f"Saved {pdf_file}")
    except Exception as e:
        log_error(f"PDF error: {e}")

# ---------- PROCESS SINGLE FILE ----------
def process_file(file, style, args):
    if not os.path.exists(file):
        log_error(f"{file} not found")
        return

    log_process(f"Processing {file}")

    # Detect language
    if file.endswith(".py"):
        lang = "python"
    elif file.endswith(".java"):
        lang = "java"
    else:
        log_error("Unsupported file type")
        return

    # Read file
    try:
        with open(file, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        log_error(f"Read error: {e}")
        return

    # API Call
    try:
        response = requests.post(API_URL, json={
            "code": code,
            "style": style,
            "language": lang
        })
    except Exception as e:
        log_error(f"API connection failed: {e}")
        return

    if response.status_code != 200:
        log_error("API request failed")
        return

    data = response.json()
    result = data.get("documented_code") or data.get("output")

    if not result:
        log_error("Invalid API response")
        return

    # ---------- TERMINAL OUTPUT ----------
    print("\n" + Fore.MAGENTA + "="*60)
    print(Fore.MAGENTA + Style.BRIGHT + "💜 GENERATED DOCUMENTATION")
    print(Fore.MAGENTA + "="*60 + "\n")
    print(Fore.MAGENTA + Style.BRIGHT + result)
    print("\n" + Fore.MAGENTA + "="*60)

    # ---------- SAVE OUTPUT ----------
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(result)
            log_success(f"Saved output to {args.out}")
        except Exception as e:
            log_error(f"Save error: {e}")

    # ---------- EXPORT FORMATS ----------
    html_file = None
    if args.md:
        save_markdown(result, file)
    if args.html or args.pdf:
        html_file = save_html(result, file, style)
    if args.pdf and html_file:
        save_pdf(html_file)

# ---------- MAIN ----------
def main():
    parser = argparse.ArgumentParser(description="🔥 Violet DocGen CLI")
    parser.add_argument("path", nargs="?", help="File or folder path")
    parser.add_argument("--style", default="google", help="Style: google/numpy/sphinx")
    parser.add_argument("--md", action="store_true", help="Export Markdown")
    parser.add_argument("--html", action="store_true", help="Export HTML")
    parser.add_argument("--pdf", action="store_true", help="Export PDF")
    parser.add_argument("--batch", action="store_true", help="Process folder")
    parser.add_argument("--out", help="Save output to file")
    args = parser.parse_args()

    # Interactive mode
    if not args.path:
        log_info("Interactive Mode")
        args.path = input("Enter file/folder path: ")
        args.style = input("Style (google/numpy/sphinx): ") or "google"

    # Batch mode
    if args.batch:
        if not os.path.isdir(args.path):
            log_error("Batch mode requires a folder path")
            return
        files = [f for f in os.listdir(args.path) if f.endswith((".py", ".java"))]
        if not files:
            log_error("No valid files found in folder")
            return
        log_info(f"Processing {len(files)} files...")
        for file in tqdm(files):
            full_path = os.path.join(args.path, file)
            process_file(full_path, args.style, args)
    else:
        process_file(args.path, args.style, args)

# ---------- RUN ----------
if __name__ == "__main__":
    main()