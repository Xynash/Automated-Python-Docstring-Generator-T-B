import sys
import os
import ast
import streamlit as st

# ---------------- FIX PROJECT ROOT PATH ----------------
# This ensures that 'app' is recognized as a module regardless of where you run it
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ---------------- INTERNAL IMPORTS ----------------
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.ai_docstring_engine import generate_ai_docstring
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Pro Python DocGen",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CUSTOM CSS (Enhanced) ----------
st.markdown("""
<style>
    html, body, [class*="st-emotion-cache"] {
        background-color: #0b0f0e;
        color: #e6fff3;
    }
    .stApp {
        background: #0b0f0e;
    }
    .hero {
        text-align: center;
        padding: 2rem 0rem;
    }
    .hero h1 {
        font-size: 3.5rem;
        background: linear-gradient(90deg, #00ff9c, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero p {
        font-size: 1.2rem;
        color: #88a098;
    }
    .upload-card {
        background: #111817;
        border: 1px solid #1e2b28;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #00ff9c, #00d4ff);
        color: #001b14;
        border: none;
        padding: 0.75rem;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 255, 156, 0.3);
    }
    code {
        color: #00ff9c !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <h1>🐍 Pro Docstring Generator</h1>
    <p>AI-Powered Documentation Engine for Junior Engineers</p>
</div>
""", unsafe_allow_html=True)

# ---------- MAIN UI ----------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop your Python file here",
    type=["py"],
    help="The system will analyze all functions and classes within the file."
)

col_toggle, col_btn = st.columns([1, 1])

with col_toggle:
    use_ai = st.toggle("🚀 Enable AI Analysis (GPT-4o-mini)", value=True)
    st.caption("AI mode analyzes logic; Heuristic mode uses standard templates.")

with col_btn:
    generate = st.button("✨ Start Documentation Pipeline")

st.markdown('</div>', unsafe_allow_html=True)

# ---------- CORE PROCESSING PIPELINE ----------
if uploaded_file and generate:
    try:
        # Step 1: Load code
        original_code = uploaded_file.read().decode("utf-8")
        updated_code = original_code
        
        # Step 2: Extract all functions (including class methods)
        with st.spinner("Analyzing code structure with AST..."):
            functions_to_process = extract_functions(original_code)
        
        if not functions_to_process:
            st.warning("No functions or classes found in this file.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, func_info in enumerate(functions_to_process):
                func_name = func_info["name"]
                status_text.text(f"Processing: {func_name}...")
                
                # Check if it already has a docstring
                if func_info["docstring"]:
                    continue

                # Step 3: Extract deeper metadata (Type hints, logic, scope)
                func_metadata = analyze_function(
                    func_info["node"], 
                    class_name=func_info["class_name"]
                )

                # Step 4: Generate Docstring
                doc = ""
                if use_ai:
                    try:
                        # Now passes the rich metadata dictionary
                        doc = generate_ai_docstring(func_metadata)
                    except Exception as ai_err:
                        st.error(f"AI Error for {func_name}: {ai_err}")
                        doc = generate_docstring(func_metadata) # Fallback
                else:
                    doc = generate_docstring(func_metadata)

                # Step 5: Safely insert into code
                updated_code = insert_docstring(updated_code, func_metadata, doc)
                
                # Update progress
                progress = (index + 1) / len(functions_to_process)
                progress_bar.progress(progress)

            status_text.text("✅ Documentation complete!")

            # ---------- RESULTS DISPLAY ----------
            st.divider()
            
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("📄 Original Source")
                st.code(original_code, language="python")

            with col_right:
                st.subheader("⚡ Documented Output")
                st.code(updated_code, language="python")

            # ---------- DOWNLOAD ----------
            st.divider()
            st.download_button(
                label="📥 Download Documented File",
                data=updated_code,
                file_name=f"documented_{uploaded_file.name}",
                mime="text/plain",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Pipeline Failure: {str(e)}")
        st.info("Check if your Python file has syntax errors.")

elif uploaded_file:
    st.info("File uploaded. Click the button above to begin.")