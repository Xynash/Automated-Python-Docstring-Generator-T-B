import sys
import os
import ast
import streamlit as st

# ---------------- FIX IMPORT CACHE ISSUE ----------------
sys.modules.pop("app.core.ai_engine", None)

# ---------------- FIX PROJECT ROOT PATH ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ---------------- INTERNAL IMPORTS ----------------
#from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
from app.core.ai_engine import analyze_function

# COMMENTED OUT TO AVOID ERRORS SINCE OPENAI IS NOT INSTALLED
from app.core.ai_docstring_engine import generate_ai_docstring


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Docstring Generator (Local Mode)",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0b0f0e;
    color: #e6fff3;
    font-family: 'Segoe UI', sans-serif;
}
.hero { text-align: center; padding: 2rem; }
.hero h1 { font-size: 3rem; color: #00ff9c; }
.upload-card { background: #111817; border-radius: 16px; padding: 2rem; }
.stButton > button {
    background: linear-gradient(90deg, #00ff9c, #00d4ff);
    color: #001b14; border-radius: 12px; font-weight: 600; width: 100%;
}
pre { background-color: #050807 !important; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


# ---------- HERO ----------
st.markdown("""
<div class="hero">
<h1>🐍 Docstring Generator</h1>
<p>AST-powered Local Documentation Engine</p>
</div>
""", unsafe_allow_html=True)


# ---------- UPLOAD ----------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload a Python (.py) file",
    type=["py"]
)


style = st.selectbox(
    "📝 Docstring Style",
    ["Google", "NumPy", "Sphinx", "JSDoc", "Javadoc", "Doxygen"],
    help="Choose the documentation style for generated docstrings"
)

language = st.selectbox(
    "🌐 Language",
    ["python", "javascript", "java", "cpp"],
    help="Select the programming language of the uploaded file"
)
generate = st.button("✨ Generate Docstrings")

st.markdown('</div>', unsafe_allow_html=True)


# ---------- PROCESS ----------
if uploaded_file and generate:

    try:
        code = uploaded_file.read().decode("utf-8")
        updated_code = code

        # Parse AST
        tree = ast.parse(code)

        # Extract functions
        functions = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]

        for node in functions:
            func_data = analyze_function(node)

            # Skip if docstring exists
            if func_data["docstring"]:
                continue

            doc = generate_ai_docstring(func_data, style=style, language=language)
            # Insert docstring safely
            updated_code = insert_docstring(updated_code, func_data, doc)

        # ---------- STATUS ----------
        
        st.success(f"✨ Docstrings generated!")
        # ---------- OUTPUT ----------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📄 Original Code")
            st.code(code, language="python")

        with col2:
            st.markdown("### ⚡ Generated Code")
            st.code(updated_code, language="python")

        # ---------- DOWNLOAD ----------
        st.download_button(
            "⬇ Download Updated File",
            data=updated_code,
            file_name=f"updated_{uploaded_file.name}",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")


elif uploaded_file:
    st.info("Click **Generate Docstrings** to continue.")