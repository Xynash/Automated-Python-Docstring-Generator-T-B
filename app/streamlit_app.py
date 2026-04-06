import sys
import os
import time
import psutil
import pandas as pd
import plotly.express as px
import streamlit as st
import zipfile
import io

# ---------- SESSION STATE ----------
if "review_results" not in st.session_state:
    st.session_state.review_results = None
if "readme_result" not in st.session_state:
    st.session_state.readme_result = None
if "doc_results" not in st.session_state:
    st.session_state.doc_results = None
if "original_code" not in st.session_state:
    st.session_state.original_code = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_code" not in st.session_state:
    st.session_state.chat_code = None
if "telemetry" not in st.session_state:
    st.session_state.telemetry = {"time": 0.0, "files": 0, "mem": 0.0}
    
# ---------------- FIX PROJECT ROOT PATH ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ---------------- INTERNAL IMPORTS ----------------
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
from app.core.ai_docstring_engine import generate_ai_docstring
from app.core.code_reviewer import review_code
from app.core.readme_generator import generate_readme
from app.core.chat_engine import chat_with_code
from app.core.prompt_builder import detect_language

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Docgen : Universal AI Platform",
    page_icon="🌐",
    layout="wide"
)

# ---------- ADVANCED CUSTOM CSS ----------
st.markdown("""
<style>
    html, body, [class*="css"] {
        background-color: #0b0f0e;
        color: #e6fff3;
        font-family: 'Segoe UI', sans-serif;
    }
    .hero { text-align: center; padding: 1rem 0rem; }
    .hero h1 { 
        font-size: 3.5rem; 
        background: linear-gradient(90deg, #00ff9c, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .upload-card { 
        background: rgba(17, 24, 23, 0.7); 
        border: 1px solid rgba(0, 255, 156, 0.2); 
        border-radius: 16px; 
        padding: 2rem; 
        margin-bottom: 20px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00ff9c, #00d4ff);
        color: #001b14; border-radius: 12px; font-weight: 700; border: none;
    }
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 156, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🌐 Docgen AI</h1><p>Universal AI Code-Intelligence Platform</p></div>', unsafe_allow_html=True)

# ---------- UPLOAD ----------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Upload Source Files or a Project ZIP", 
    type=["py", "js", "java", "cpp", "c", "zip"], 
    accept_multiple_files=True
)

col_a, col_b = st.columns(2)
with col_a:
    use_ai = st.toggle("🚀 Enable AI Logical Analysis", value=True)
with col_b:
    doc_style = st.selectbox("Documentation Style", ["google", "numpy", "sphinx"])
st.markdown('</div>', unsafe_allow_html=True)

# ---------- ANALYTICS ROW ----------
if st.session_state.original_code:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⚡ Latency", f"{st.session_state.telemetry['time']}s")
    m2.metric("🧠 RAM Usage", f"{st.session_state.telemetry['mem']} MB")
    m3.metric("📂 Files", st.session_state.telemetry['files'])
    m4.metric("🛡️ Security Score", "A+" if not st.session_state.review_results else "B")

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["✨ Documentation Engine", "🔍 Quality Audit & Viz", "📄 README Architect"])

# ---------- TAB 1: DOCUMENTATION GENERATOR ----------
with tab1:
    generate = st.button("✨ Execute Documentation Pipeline", key="gen_btn")

    if uploaded_files and generate:
        try:
            start_time = time.perf_counter()
            process = psutil.Process(os.getpid())
            start_mem = process.memory_info().rss / (1024 * 1024)
            
            combined_original = ""
            combined_updated = ""
            file_count = 0

            # --- NEW INTERACTIVE STATUS ---
            with st.status("🚀 Orchestrating AI Pipeline...", expanded=True) as status:
                st.write("📂 Extracting Workspace...")
                for uploaded_file in uploaded_files:
                    to_process = []
                    if uploaded_file.name.endswith('.zip'):
                        with zipfile.ZipFile(uploaded_file) as z:
                            for fpath in z.namelist():
                                if fpath.endswith(('.py', '.js', '.java', '.cpp', '.c')):
                                    with z.open(fpath) as f:
                                        to_process.append((fpath, f.read().decode("utf-8")))
                    else:
                        to_process.append((uploaded_file.name, uploaded_file.read().decode("utf-8")))

                    for filename, code in to_process:
                        file_count += 1
                        st.write(f"⚙️ Parsing Node Map: `{filename}`")
                        updated_code = code
                        lang = detect_language(code)
                        functions = extract_functions(code, language=lang)
                        
                        if functions:
                            for func_info in functions:
                                if func_info["docstring"]: continue
                                meta = analyze_function(func_info["node"], class_name=func_info["class_name"]) if func_info.get("node") else analyze_function(func_info)
                                doc = generate_ai_docstring(meta, style=doc_style, language=lang) if use_ai else generate_docstring(meta)
                                updated_code = insert_docstring(updated_code, meta, doc)

                        combined_original += f"\n# FILE: {filename}\n" + code + "\n"
                        combined_updated += f"\n# FILE: {filename}\n" + updated_code + "\n"

                status.update(label="✅ Pipeline Execution Complete", state="complete")

            st.session_state.doc_results = combined_updated
            st.session_state.original_code = combined_original
            st.session_state.chat_code = combined_original
            st.session_state.telemetry = {
                "time": round(time.perf_counter() - start_time, 3),
                "files": file_count,
                "mem": round((process.memory_info().rss / (1024 * 1024)) - start_mem, 2)
            }

        except Exception as e:
            st.error(f"Execution Error: {e}")

    if st.session_state.doc_results:
        c1, c2 = st.columns(2)
        with c1: st.markdown("### 📄 Original"); st.code(st.session_state.original_code)
        with c2: st.markdown("### ⚡ Documented"); st.code(st.session_state.doc_results)

# ---------- TAB 2: REVIEWER (WITH DATA VISUALIZATION) ----------
with tab2:
    if st.button("🔍 Run Logic-Aware Audit", key="review_btn"):
        if st.session_state.original_code:
            with st.spinner("Analyzing code quality..."):
                st.session_state.review_results = review_code(st.session_state.original_code)
        else: st.warning("Please upload code first.")

    if st.session_state.review_results:
        rev = st.session_state.review_results
        
        # --- DATA VISUALIZATION PART ---
        st.markdown("### 📊 Quality Distribution Analytics")
        plot_col, stats_col = st.columns([2, 1])
        
        with plot_col:
            # Prepare data for Plotly
            data = {
                "Category": ["Bugs", "Security", "Performance", "Best Practices"],
                "Count": [len(rev.get('bugs', [])), len(rev.get('security', [])), 
                          len(rev.get('performance', [])), len(rev.get('best_practices', []))]
            }
            df = pd.DataFrame(data)
            fig = px.bar(df, x='Category', y='Count', color='Category', 
                         title="Detected Issues by Category", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        with stats_col:
            st.write("#### 🛡️ Executive Summary")
            st.info(rev.get("summary", "Analysis complete."))
            total_issues = sum(data["Count"])
            st.metric("Total Issues Detected", total_issues, delta=total_issues, delta_color="inverse")

        st.divider()
        # Display detailed expanders for bugs/security...
        for cat in ["bugs", "security"]:
            st.markdown(f"#### Detailed {cat.title()}")
            for item in rev.get(cat, []):
                with st.expander(f"📍 {item.get('issue')}"):
                    st.code(f"Fix: {item.get('fix')}")

# ---------- TAB 3: README GENERATOR ----------
with tab3:
    if st.button("📄 Generate README", key="readme_btn"):
        if st.session_state.original_code:
            with st.spinner("Generating documentation..."):
                st.session_state.readme_result = generate_readme(st.session_state.original_code, "Workspace")
        else: st.warning("Upload code first.")

    if st.session_state.readme_result:
        st.markdown("### 📝 Project README.md")
        st.code(st.session_state.readme_result, language="markdown")

# ---------- SIDEBAR CHAT ----------
with st.sidebar:
    st.markdown("## 💬 Code Chat")
    if st.session_state.chat_code:
        st.success("✅ Context Synced")
        for msg in st.session_state.chat_messages:
            st.chat_message(msg["role"]).write(msg["content"])
        
        if prompt := st.chat_input("Ask about your logic:"):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            with st.spinner("Thinking..."):
                response = chat_with_code(st.session_state.chat_messages, st.session_state.chat_code, st.session_state.doc_results, st.session_state.review_results)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()
    else:
        st.info("Upload code to start chat.")