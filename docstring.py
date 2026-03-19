import re
import os
import argparse
import pdfkit
from colorama import Fore, init

init(autoreset=True)

WKHTML_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# ---------- LOGS ----------
def log_info(msg): print(Fore.YELLOW + "[INFO] " + msg)
def log_success(msg): print(Fore.CYAN + "[SUCCESS] " + msg)
def log_error(msg): print(Fore.RED + "[ERROR] " + msg)
def log_warning(msg): print(Fore.MAGENTA + "[WARNING] " + msg)

# ---------- GENERATOR ----------
def generate_docs(code, style, ext):
    docs = []

    # ---- C / C++ ----
    if ext in ["c", "cpp"]:
        pattern = r'(int|float|double|void|char|bool|string)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        functions = re.findall(pattern, code)

    # ---- JS ----
    elif ext == "js":
        pattern = r'function\s+(\w+)\s*\(([^)]*)\)'
        matches = re.findall(pattern, code)
        functions = [("", name, params) for name, params in matches]

    else:
        return ""

    # ---- Generate ----
    for return_type, func_name, params in functions:

        params_list = []
        if params.strip():
            params_list = [p.strip() for p in params.split(",")]

        if style == "sphinx":
            doc = "/**\n"
            doc += f" * {func_name} function\n"
            for p in params_list:
                doc += f" * :param {p}: description\n"
            doc += " * :return: value\n */\n"

        elif style == "jsdoc":
            doc = "/**\n"
            doc += f" * {func_name} function\n"
            for p in params_list:
                doc += f" * @param {{any}} {p}\n"
            doc += " * @returns {any}\n */\n"

        else:  # doxygen default
            doc = "/**\n"
            doc += f" * {func_name} function\n"
            for p in params_list:
                doc += f" * @param {p}\n"
            doc += " * @return value\n */\n"

        docs.append(doc + f"{func_name}({params})\n")

    return "\n".join(docs)

# ---------- COLOR ----------
def colorize(text):
    text = Fore.CYAN + text
    text = text.replace("@param", Fore.YELLOW + "@param" + Fore.CYAN)
    text = text.replace("@return", Fore.RED + "@return" + Fore.CYAN)
    text = text.replace(":param", Fore.YELLOW + ":param" + Fore.CYAN)
    return text

# ---------- SAVE ----------
def save_md(content, file):
    path = file + "_doc.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Documentation\n\n```\n{content}\n```")
    log_success(f"Saved {path}")

def save_html(content, file, style):
    path = file + "_doc.html"

    html = f"""
<html>
<head>
<meta charset="UTF-8">
<style>
body {{background:#1e1e1e;color:white;font-family:Arial;padding:20px;}}
pre {{background:#2d2d2d;padding:20px;border-radius:10px;color:#4FC3F7;}}
</style>
</head>
<body>
<h2>Documentation ({style})</h2>
<pre>{content}</pre>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    log_success(f"Saved {path}")
    return path

def save_pdf(html):
    pdf = html.replace(".html", ".pdf")
    try:
        config = pdfkit.configuration(wkhtmltopdf=WKHTML_PATH)
        pdfkit.from_file(html, pdf, configuration=config)
        log_success(f"Saved {pdf}")
    except Exception as e:
        log_error(f"PDF error: {e}")

# ---------- PROCESS ----------
def process_file(file, style, args):
    if not os.path.exists(file):
        log_error(f"{file} not found")
        return

    ext = file.split(".")[-1]

    # auto style
    if style == "auto":
        style = "jsdoc" if ext == "js" else "doxygen"

    if ext in ["c", "cpp", "js"] and style == "sphinx":
        log_warning("Sphinx is custom for this language")

    with open(file, encoding="utf-8") as f:
        code = f.read()

    log_info(f"Processing {file}")

    result = generate_docs(code, style, ext)

    if not result.strip():
        log_warning("No functions found")
        return

    print("\n" + "="*50)
    print(colorize(result))
    print("="*50)

    html = None
    if args.md:
        save_md(result, file)
    if args.html or args.pdf:
        html = save_html(result, file, style)
    if args.pdf and html:
        save_pdf(html)

# ---------- MAIN ----------
def main():
    parser = argparse.ArgumentParser(description="DocString Generator")

    parser.add_argument("path", nargs="?", help="file or folder")
    parser.add_argument("--style", default="auto")
    parser.add_argument("--md", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    parser.add_argument("--batch", action="store_true")

    args = parser.parse_args()

    if not args.path:
        args.path = input("Enter file/folder: ")

    # ---- batch ----
    if args.batch:
        if not os.path.isdir(args.path):
            log_error("Batch requires folder")
            return

        files = []
        for root, _, names in os.walk(args.path):
            for f in names:
                if f.endswith((".c", ".cpp", ".js")):
                    files.append(os.path.join(root, f))

        if not files:
            log_error("No valid files found")
            return

        log_info(f"Processing {len(files)} files")

        for f in files:
            process_file(f, args.style, args)

    else:
        process_file(args.path, args.style, args)

# ---------- RUN ----------
if __name__ == "__main__":
    main()