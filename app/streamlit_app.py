import sys
import os
import ast
import streamlit as st

# ---------------- FIX PROJECT ROOT PATH ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ---------------- INTERNAL IMPORTS ----------------
from app.core.parser import extract_functions
from app.core.ai_engine import analyze_function
from app.core.docstring_gen import generate_docstring
from app.core.inserter import insert_docstring
from app.core.ai_docstring_engine import generate_ai_docstring # RE-ENABLED

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Docstring Generator",
    page_icon="🐍",
    layout="wide"
)

# ---------- CUSTOM CSS (Original) ----------
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

st.markdown('<div class="hero"><h1>🐍 AI Docstring Generator</h1><p>Intelligent Python Documentation Engine</p></div>', unsafe_allow_html=True)

# ---------- UPLOAD ----------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a Python (.py) file", type=["py"])

# RE-ENABLED: AI Toggle and Style Selector
col_a, col_b = st.columns(2)
with col_a:
    use_ai = st.toggle("🚀 Enable AI Analysis (Groq/Llama 3.3)", value=True)
with col_b:
    doc_style = st.selectbox("Style Preference", ["google", "numpy", "sphinx"])

generate = st.button("✨ Generate Docstrings")
st.markdown('</div>', unsafe_allow_html=True)

# ---------- PROCESS ----------
if uploaded_file and generate:
    try:
        code = uploaded_file.read().decode("utf-8")
        updated_code = code

        with st.spinner("Analyzing code structure and generating docstrings..."):
            functions = extract_functions(code)

            if not functions:
                st.warning("No functions found.")
            else:
                for func_info in functions:
                    if func_info["docstring"]: continue

                    # Get metadata
                    func_metadata = analyze_function(func_info["node"], class_name=func_info["class_name"])

                    # Logic: AI with Fallback
                    if use_ai:
                        try:
                            # Use the real AI Engine
                            doc = generate_ai_docstring(func_metadata, style=doc_style)
                            is_ai = True
                        except Exception as e:
                            st.error(f"AI failed for {func_info['name']}: {e}")
                            doc = generate_docstring(func_metadata)
                            is_ai = False
                    else:
                        doc = generate_docstring(func_metadata)
                        is_ai = False

                    # Insert into code
                    updated_code = insert_docstring(updated_code, func_metadata, doc)

                # Status Message
                mode_text = "AI Mode" if is_ai else "Local Heuristic Mode"
                st.success(f"✨ Docstrings generated successfully using {mode_text}!")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 📄 Original")
                    st.code(code, language="python")
                with col2:
                    st.markdown("### ⚡ Documented")
                    st.code(updated_code, language="python")

                st.download_button("⬇ Download File", data=updated_code, file_name=f"doc_{uploaded_file.name}")

    except Exception as e:
        st.error(f"Error: {e}")