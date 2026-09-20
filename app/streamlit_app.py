import io
import math
import os
import sys
import time
import zipfile

import pandas as pd
import plotly.express as px
import psutil
import streamlit as st

# ---------- PAGE CONFIG (must be the first Streamlit call) ----------
st.set_page_config(page_title="Docgen AI", page_icon="🌐", layout="wide")

# ---------- PROJECT ROOT PATH ----------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ---------- INTERNAL IMPORTS ----------
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
from app.core.ai_docstring_engine import MODEL, generate_ai_docstring
from app.core.code_reviewer import review_code
from app.core.readme_generator import generate_readme
from app.core.chat_engine import chat_with_code
from app.core.prompt_builder import detect_language

# ---------- CONSTANTS ----------
LANG_BY_EXT = {"py": "python", "js": "javascript", "java": "java", "c": "c", "cpp": "cpp"}
CODE_EXTS = tuple("." + e for e in LANG_BY_EXT)
SKIP_PARTS = {"__MACOSX", "node_modules", ".git", ".venv", "venv", "__pycache__"}
MAX_FILES = 25
CHAT_SUGGESTIONS = [
    "Which function is the riskiest?",
    "Explain this code in simple terms",
    "What tests should I write first?",
]
CATEGORY_COLORS = {
    "Bugs": "#ff6b6b",
    "Security": "#ffb454",
    "Performance": "#00d4ff",
    "Best Practices": "#00ff9c",
}

EXAMPLE_BEFORE = '''def calculate_discount(price, percent):
    discounted = price - (price * percent / 100)
    return round(discounted, 2)'''

EXAMPLE_AFTER = '''def calculate_discount(price, percent):
    """Return the price after a discount.

    Args:
        price (float): Original price.
        percent (float): Discount in percent.

    Returns:
        float: Discounted price, rounded.

    Example:
        >>> calculate_discount(100.0, 15)
        85.0
    """
    discounted = price - (price * percent / 100)
    return round(discounted, 2)'''

SAMPLE_CODE = '''import sqlite3


def average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total / len(numbers)


def get_user(db_path, user_id):
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    return conn.execute(query).fetchone()


def run_expression(expr):
    return eval(expr)


class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name, price, quantity=1):
        self.items.append({"name": name, "price": price, "quantity": quantity})

    def total(self):
        return sum(i["price"] * i["quantity"] for i in self.items)
'''
SAMPLE_SOURCES = [("example.py", SAMPLE_CODE)]


# ---------- SESSION STATE ----------
def init_state():
    defaults = {
        "review_results": None,
        "readme_result": None,
        "doc_results": None,
        "original_code": None,
        "chat_code": None,
        "doc_files": {},
        "skipped": [],
        "chat_messages": [],
        "telemetry": {"time": 0.0, "mem": 0.0, "files": 0, "functions": 0, "fallbacks": 0},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

# ---------- STYLE ----------
st.markdown(
    """
<style>
    .block-container { padding-top: 2.2rem; max-width: 1180px; }
    .hero { text-align: center; padding: 0.25rem 0 1.5rem; }
    .hero h1 {
        font-size: 3rem; font-weight: 800; letter-spacing: -0.02em; margin: 0;
        background: linear-gradient(90deg, #00ff9c, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero p {
        color: #8fb3a4; max-width: 640px; margin: 0.6rem auto 0;
        font-size: 1.05rem; line-height: 1.5;
    }
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(90deg, #00ff9c, #00d4ff);
        color: #001b14; border: none; border-radius: 10px; font-weight: 700;
    }
    .stButton > button:hover:not(:disabled), .stDownloadButton > button:hover { filter: brightness(1.08); }
    .stButton > button:disabled {
        background: #17201e; color: #6f8f82; opacity: 1;
        border: 1px solid rgba(0, 255, 156, 0.15);
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%; text-align: left; background: transparent; color: #e6fff3;
        border: 1px solid rgba(0, 255, 156, 0.25); font-weight: 500;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(0, 255, 156, 0.14);
        border-radius: 10px; padding: 0.8rem 1rem;
    }
    footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------- HELPERS ----------
def show_code(code, language="python", line_numbers=True):
    """Show code with wrapping (and optional line numbers) when this Streamlit version supports it."""
    try:
        st.code(code, language=language, line_numbers=line_numbers, wrap_lines=True)
    except TypeError:
        st.code(code, language=language)


def show_chart(fig):
    """Stretch the chart to the column width on both new and older Streamlit versions."""
    try:
        st.plotly_chart(fig, width="stretch")
    except Exception:
        st.plotly_chart(fig, use_container_width=True)


def file_language(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "py"
    return LANG_BY_EXT.get(ext, "python")


def collect_sources(files):
    """Read uploads (and ZIP contents) into [(name, code)], plus a list of skipped items."""
    sources, skipped = [], []
    for uf in files:
        raw = uf.getvalue()
        if uf.name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    for info in z.infolist():
                        path = info.filename
                        if info.is_dir() or not path.lower().endswith(CODE_EXTS):
                            continue
                        if any(part in SKIP_PARTS for part in path.split("/")):
                            continue
                        try:
                            sources.append((path, z.read(info).decode("utf-8")))
                        except UnicodeDecodeError:
                            skipped.append(f"{path} (not UTF-8)")
            except zipfile.BadZipFile:
                skipped.append(f"{uf.name} (not a valid ZIP)")
        else:
            try:
                sources.append((uf.name, raw.decode("utf-8")))
            except UnicodeDecodeError:
                skipped.append(f"{uf.name} (not UTF-8)")
    return sources, skipped


def document_sources(sources, use_ai, style, status, skipped):
    """Run parse -> generate -> insert for every source file."""
    files, n_funcs, n_fallbacks = {}, 0, 0
    for filename, code in sources:
        try:
            lang = detect_language(code)
            functions = extract_functions(code, language=lang)
            pending = [f for f in functions if not f["docstring"]]
            status.write(f"⚙️ `{filename}`: {len(functions)} functions found, {len(pending)} need docs")

            updated = code
            for i, fn in enumerate(pending, 1):
                status.write(f"✍️ Documenting `{fn['name']}` ({i}/{len(pending)})")
                if fn.get("node"):
                    meta = analyze_function(fn["node"], class_name=fn["class_name"])
                else:
                    meta = analyze_function(fn)
                if use_ai:
                    try:
                        doc = generate_ai_docstring(meta, style=style, language=lang)
                    except Exception:
                        doc = generate_docstring(meta, style)
                        n_fallbacks += 1
                else:
                    doc = generate_docstring(meta, style)
                updated = insert_docstring(updated, meta, doc)
                n_funcs += 1
            outline = [
                {"name": f["name"], "class": f.get("class_name"), "had_doc": bool(f["docstring"])}
                for f in functions
            ]
            files[filename] = {"orig": code, "new": updated, "lang": file_language(filename), "outline": outline}
        except Exception as e:
            skipped.append(f"{filename} ({type(e).__name__}: {e})")
    return files, n_funcs, n_fallbacks


def build_download(files):
    if len(files) == 1:
        name, d = next(iter(files.items()))
        return d["new"].encode("utf-8"), f"documented_{os.path.basename(name)}", "text/plain"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, d in files.items():
            z.writestr(name, d["new"])
    return buf.getvalue(), "documented_project.zip", "application/zip"


def health_grade(rev):
    """Heuristic grade: weighted count of findings from the audit."""
    points = (
        len(rev.get("security", [])) * 4
        + len(rev.get("bugs", [])) * 3
        + len(rev.get("performance", [])) * 1.5
        + len(rev.get("best_practices", [])) * 0.5
    )
    score = max(0, round(100 - points * 2))
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"
    return grade, score


GRAPH_STYLE = {
    "project": {"name": "Project", "color": "#e6fff3", "size": 8, "symbol": "circle"},
    "file": {"name": "File", "color": "#00d4ff", "size": 9, "symbol": "diamond"},
    "class": {"name": "Class", "color": "#b48cff", "size": 7, "symbol": "square"},
    "new": {"name": "Documented by Docgen", "color": "#00ff9c", "size": 5, "symbol": "circle"},
    "old": {"name": "Already documented", "color": "#6f8f82", "size": 5, "symbol": "circle"},
}


def sphere_points(n, radius):
    """Spread n points evenly on a sphere (Fibonacci sphere)."""
    points = []
    for i in range(n):
        phi = math.pi / 2 if n == 1 else math.acos(1 - 2 * (i + 0.5) / n)
        theta = math.pi * (1 + 5 ** 0.5) * i
        points.append((
            radius * math.sin(phi) * math.cos(theta),
            radius * math.sin(phi) * math.sin(theta),
            radius * math.cos(phi),
        ))
    return points


def build_project_graph(files):
    """Build a 3D graph: project -> files -> classes -> functions. Returns (figure, stats)."""
    import plotly.graph_objects as go

    nodes, edges = [], []

    def add(kind, label, hover, pos):
        nodes.append({"kind": kind, "label": label, "hover": hover, "pos": pos})
        return len(nodes) - 1

    def add_func(item, fname, pos, cname):
        kind = "old" if item["had_doc"] else "new"
        status = "Already documented" if item["had_doc"] else "Documented by Docgen"
        prefix = f"{cname}." if cname else ""
        return add(kind, "", f"{prefix}{item['name']}()<br>{status}<br>{fname}", pos)

    root = add("project", "", "Project", (0.0, 0.0, 0.0))
    n_files = len(files)
    ring = max(5.0, 0.9 * n_files)

    for k, (fname, d) in enumerate(files.items()):
        angle = 2 * math.pi * k / max(n_files, 1)
        fpos = (ring * math.cos(angle), ring * math.sin(angle), 1.5 * math.sin(k * 1.7))
        fi = add("file", os.path.basename(fname), f"File: {fname}", fpos)
        edges.append((root, fi))

        by_class, loose = {}, []
        for item in d.get("outline", []):
            if item.get("class"):
                by_class.setdefault(item["class"], []).append(item)
            else:
                loose.append(item)
        children = [("class", c, ms) for c, ms in by_class.items()] + [("func", None, it) for it in loose]
        offsets = sphere_points(len(children), 1.4 + 0.25 * math.sqrt(len(children)))

        for (kind, cname, payload), off in zip(children, offsets):
            cpos = (fpos[0] + off[0], fpos[1] + off[1], fpos[2] + off[2])
            if kind == "class":
                ci = add("class", cname, f"Class: {cname}<br>{fname}<br>{len(payload)} method(s)", cpos)
                edges.append((fi, ci))
                m_offsets = sphere_points(len(payload), 0.7 + 0.2 * math.sqrt(len(payload)))
                for m, moff in zip(payload, m_offsets):
                    mpos = (cpos[0] + moff[0], cpos[1] + moff[1], cpos[2] + moff[2])
                    edges.append((ci, add_func(m, fname, mpos, cname)))
            else:
                edges.append((fi, add_func(payload, fname, cpos, None)))

    ex, ey, ez = [], [], []
    for a, b in edges:
        ex += [nodes[a]["pos"][0], nodes[b]["pos"][0], None]
        ey += [nodes[a]["pos"][1], nodes[b]["pos"][1], None]
        ez += [nodes[a]["pos"][2], nodes[b]["pos"][2], None]

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode="lines", hoverinfo="none", showlegend=False,
                               line=dict(color="rgba(143,179,164,0.35)", width=2)))
    for kind, style in GRAPH_STYLE.items():
        subset = [n for n in nodes if n["kind"] == kind]
        if not subset:
            continue
        fig.add_trace(go.Scatter3d(
            x=[n["pos"][0] for n in subset], y=[n["pos"][1] for n in subset], z=[n["pos"][2] for n in subset],
            mode="markers+text" if kind == "file" else "markers",
            text=[n["label"] for n in subset], textposition="top center",
            hovertext=[n["hover"] for n in subset], hoverinfo="text",
            marker=dict(size=style["size"], color=style["color"], symbol=style["symbol"]),
            name=style["name"], showlegend=kind != "project",
        ))
    hidden_axis = dict(visible=False)
    fig.update_layout(
        template="plotly_dark", height=560, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(xaxis=hidden_axis, yaxis=hidden_axis, zaxis=hidden_axis,
                   bgcolor="rgba(0,0,0,0)", aspectmode="data"),
        legend=dict(orientation="h", y=0.02, x=0.5, xanchor="center"),
    )
    stats = {
        "files": n_files,
        "classes": sum(1 for n in nodes if n["kind"] == "class"),
        "functions": sum(1 for n in nodes if n["kind"] in ("new", "old")),
        "new": sum(1 for n in nodes if n["kind"] == "new"),
        "old": sum(1 for n in nodes if n["kind"] == "old"),
    }
    return fig, stats


def landing():
    st.markdown("#### See what you get")
    left, right = st.columns([5, 7])
    with left:
        st.caption("Before")
        show_code(EXAMPLE_BEFORE, "python", line_numbers=False)
        st.markdown("**Docstrings that match the code**  \nWritten from each function's actual logic in Google, NumPy or Sphinx style. Functions that already have docs are skipped.")
        st.markdown("**A review you can act on**  \nBugs, security risks and performance issues, with line numbers and suggested fixes.")
        st.markdown("**Answers, not just files**  \nDraft a README and ask questions about your code in the sidebar chat.")
    with right:
        st.caption("After (Google style)")
        show_code(EXAMPLE_AFTER, "python", line_numbers=False)

    st.caption(
        "Works with Python, Java, JavaScript, C and C++. AI features send your code to Groq. "
        "Turn off AI Logical Analysis to get local template docstrings; the audit, README and chat always use AI."
    )


# ---------- HERO ----------
st.markdown(
    '<div class="hero"><h1>🌐 Docgen AI</h1>'
    "<p>Upload code. Get docstrings, a bug and security review, a README, "
    "and answers about how it works.</p></div>",
    unsafe_allow_html=True,
)

# ---------- UPLOAD ----------
with st.container(border=True):
    uploaded_files = st.file_uploader(
        "Upload source files or a project ZIP",
        type=["py", "js", "java", "cpp", "c", "zip"],
        accept_multiple_files=True,
        help=f"UTF-8 text files only. At most {MAX_FILES} files are processed per run.",
    )
    col_a, col_b = st.columns(2)
    with col_a:
        use_ai = st.toggle("🚀 Enable AI Logical Analysis", value=True)
    with col_b:
        doc_style = st.selectbox("Documentation style (Python)", ["google", "numpy", "sphinx"])

metrics_box = st.container()

# ---------- TABS ----------
tab1, tab2, tab3, tab4 = st.tabs(["✨ Documentation Engine", "🔍 Quality Audit", "📄 README Architect", "🗺️ Project Map"])

# ---------- TAB 1: DOCUMENTATION ----------
with tab1:
    b1, b2, _spacer = st.columns([1.3, 1.1, 3])
    run = b1.button("✨ Generate documentation", key="gen_btn", disabled=not uploaded_files)
    run_sample = b2.button("🧪 Try an example", key="sample_btn", help="Runs the pipeline on a small built-in Python file.")
    if not uploaded_files and not st.session_state.doc_files:
        st.caption("Upload a file above, or try the built-in example.")

    if run or run_sample:
        start = time.perf_counter()
        proc = psutil.Process(os.getpid())
        mem_before = proc.memory_info().rss / (1024 * 1024)
        try:
            if run_sample and not run:
                sources, skipped = list(SAMPLE_SOURCES), []
            else:
                sources, skipped = collect_sources(uploaded_files)
            if len(sources) > MAX_FILES:
                skipped += [f"{name} (over the {MAX_FILES}-file limit)" for name, _ in sources[MAX_FILES:]]
                sources = sources[:MAX_FILES]

            if not sources:
                st.error("No readable source files found. Upload .py, .js, .java, .c or .cpp files in UTF-8, or a ZIP containing them.")
            else:
                with st.status("Running documentation pipeline...", expanded=True) as status:
                    files, n_funcs, n_fallbacks = document_sources(sources, use_ai, doc_style, status, skipped)
                    status.update(label="Pipeline complete", state="complete", expanded=False)

                if files:
                    st.session_state.doc_files = files
                    st.session_state.original_code = "".join(f"\n# FILE: {n}\n{d['orig']}\n" for n, d in files.items())
                    st.session_state.doc_results = "".join(f"\n# FILE: {n}\n{d['new']}\n" for n, d in files.items())
                    st.session_state.chat_code = st.session_state.original_code
                    st.session_state.review_results = None
                    st.session_state.readme_result = None
                    st.session_state.chat_messages = []
                    st.session_state.skipped = skipped
                    st.session_state.telemetry = {
                        "time": round(time.perf_counter() - start, 2),
                        "mem": round(proc.memory_info().rss / (1024 * 1024) - mem_before, 2),
                        "files": len(files),
                        "functions": n_funcs,
                        "fallbacks": n_fallbacks,
                    }
                else:
                    st.error("None of the files could be processed: " + "; ".join(skipped))
        except Exception as e:
            st.error(f"The pipeline stopped unexpectedly: {e}")

    files = st.session_state.doc_files
    if files:
        t = st.session_state.telemetry
        st.success(f"Documented {t.get('functions', 0)} functions across {t.get('files', 0)} file(s) in {t.get('time', 0)}s.")
        if t.get("fallbacks"):
            st.warning(f"{t['fallbacks']} function(s) used template docstrings because the AI request failed. Try again or check your API key.")
        if st.session_state.skipped:
            st.warning("Skipped: " + "; ".join(st.session_state.skipped))

        data, dl_name, mime = build_download(files)
        st.download_button("⬇️ Download documented code", data, file_name=dl_name, mime=mime)
        st.caption("Python files are regenerated from their syntax tree, so comments in the original are not kept. Compare before replacing your files.")

        names = list(files)
        chosen = names[0] if len(names) == 1 else st.selectbox("File", names)
        d = files[chosen]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Original")
            show_code(d["orig"], d["lang"])
        with c2:
            st.markdown("#### Documented")
            show_code(d["new"], d["lang"])
    elif not uploaded_files:
        landing()
    else:
        st.info(f"{len(uploaded_files)} file(s) ready. Click Generate documentation.")

# ---------- TAB 2: AUDIT ----------
with tab2:
    has_code = bool(st.session_state.original_code)
    if not has_code:
        st.info("Generate documentation first. The audit reviews the code that was loaded in that step.")
    if st.button("🔍 Run audit", key="review_btn", disabled=not has_code):
        with st.spinner("Reviewing code..."):
            try:
                st.session_state.review_results = review_code(st.session_state.original_code)
            except Exception as e:
                st.error(f"The audit failed: {e}")

    rev = st.session_state.review_results
    if rev:
        counts = {
            "Bugs": len(rev.get("bugs", [])),
            "Security": len(rev.get("security", [])),
            "Performance": len(rev.get("performance", [])),
            "Best Practices": len(rev.get("best_practices", [])),
        }
        plot_col, stats_col = st.columns([2, 1])
        with plot_col:
            df = pd.DataFrame({"Category": list(counts), "Count": list(counts.values())})
            fig = px.bar(df, x="Category", y="Count", color="Category",
                         color_discrete_map=CATEGORY_COLORS, template="plotly_dark")
            fig.update_layout(showlegend=False, height=320, margin=dict(l=10, r=10, t=30, b=10),
                              title="Findings by category",
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            show_chart(fig)
        with stats_col:
            st.markdown("#### Summary")
            st.info(rev.get("summary", "Analysis complete.") or "Analysis complete.")
            st.metric("Total findings", sum(counts.values()))

        st.divider()
        labels = {
            "bugs": "🐞 Bugs",
            "security": "🛡️ Security",
            "performance": "⚡ Performance",
            "best_practices": "✅ Best practices",
        }
        cat_tabs = st.tabs([f"{label} ({len(rev.get(key, []))})" for key, label in labels.items()])
        for cat_tab, key in zip(cat_tabs, labels):
            with cat_tab:
                items = rev.get(key, [])
                if not items:
                    st.write("No findings in this category.")
                for item in items:
                    if isinstance(item, str):
                        item = {"issue": item}
                    title = f"Line {item.get('line', '?')}: {item.get('issue', '')}"
                    with st.expander(title[:120]):
                        if item.get("code") and item.get("code") != "N/A":
                            st.markdown("**Code**")
                            st.code(item["code"])
                        st.markdown("**Suggested fix**")
                        st.code(item.get("fix", "N/A"))

# ---------- TAB 3: README ----------
with tab3:
    has_code = bool(st.session_state.original_code)
    if not has_code:
        st.info("Generate documentation first. The README is drafted from the code that was loaded.")
    if st.button("📄 Generate README", key="readme_btn", disabled=not has_code):
        with st.spinner("Drafting README..."):
            try:
                names = list(st.session_state.doc_files)
                title_hint = names[0] if len(names) == 1 else "Uploaded project"
                st.session_state.readme_result = generate_readme(st.session_state.original_code, title_hint)
            except Exception as e:
                st.error(f"README generation failed: {e}")

    if st.session_state.readme_result:
        preview_tab, raw_tab = st.tabs(["Preview", "Markdown"])
        with preview_tab:
            st.markdown(st.session_state.readme_result)
        with raw_tab:
            st.code(st.session_state.readme_result, language="markdown")
        st.download_button("⬇️ Download README.md", st.session_state.readme_result,
                           file_name="README.md", mime="text/markdown")

# ---------- TAB 4: PROJECT MAP ----------
with tab4:
    map_files = st.session_state.doc_files
    if not map_files:
        st.info("Generate documentation first. The map is built from the files that were processed.")
    else:
        fig3d, gstats = build_project_graph(map_files)
        if gstats["functions"] == 0:
            st.info("No functions were detected in the uploaded files, so there is nothing to map.")
        else:
            before = round(100 * gstats["old"] / gstats["functions"])
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Files", gstats["files"])
            g2.metric("Classes", gstats["classes"])
            g3.metric("Functions", gstats["functions"])
            g4.metric("Docstring coverage", "100%", delta=f"+{100 - before}%",
                      help="Share of detected functions that have a docstring after this run, compared with before.")
            show_chart(fig3d)
            st.caption("Drag to rotate, scroll to zoom, hover a node for details. "
                       "Green functions were documented by Docgen; grey ones already had docstrings.")

# ---------- METRICS (filled last so they always match the latest run) ----------
with metrics_box:
    if st.session_state.original_code:
        t = st.session_state.telemetry
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("⚡ Latency", f"{t.get('time', 0)}s", help="Time taken by the last documentation run.")
        m2.metric("🧠 RAM", f"{t.get('mem', 0)} MB", help="Change in this process's memory during the run. Approximate.")
        m3.metric("📂 Files", t.get("files", 0))
        m4.metric("🧩 Functions", t.get("functions", 0))
        if st.session_state.review_results:
            grade, score = health_grade(st.session_state.review_results)
            m5.metric("🛡️ Health grade", f"{grade} ({score})",
                      help="Heuristic from the audit: security findings weigh most, then bugs, performance and best practices.")
        else:
            m5.metric("🛡️ Health grade", "Not audited", help="Run the audit to get a grade.")

# ---------- SIDEBAR CHAT ----------
with st.sidebar:
    st.markdown("### 💬 Code Chat")
    if st.session_state.chat_code:
        st.caption("Ask about your code, the generated docs and the audit results.")
        if not st.session_state.chat_messages:
            for i, suggestion in enumerate(CHAT_SUGGESTIONS):
                if st.button(suggestion, key=f"suggestion_{i}"):
                    st.session_state.pending_prompt = suggestion
                    st.rerun()

        for msg in st.session_state.chat_messages:
            st.chat_message(msg["role"]).write(msg["content"])

        typed = st.chat_input("Ask about your code")
        prompt = st.session_state.pop("pending_prompt", None) or typed
        if prompt:
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            with st.spinner("Thinking..."):
                try:
                    answer = chat_with_code(
                        st.session_state.chat_messages,
                        st.session_state.chat_code,
                        st.session_state.doc_results,
                        st.session_state.review_results,
                    )
                except Exception as e:
                    answer = f"The request failed: {e}"
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()

        if st.session_state.chat_messages and st.button("Clear chat", key="clear_chat"):
            st.session_state.chat_messages = []
            st.rerun()
    else:
        st.info("Generate documentation first, then ask questions about your code here.")

    st.divider()
    st.caption(f"Model: {MODEL} on Groq")