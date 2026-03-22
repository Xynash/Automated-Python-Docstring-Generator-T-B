import sys
import os
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
if "chat_input_value" not in st.session_state:
    st.session_state.chat_input_value = ""
    
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
    page_title="Docgen : Automated Universal Docstring Generator",
    page_icon="🐍",
    layout="wide"
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

st.markdown('<div class="hero"><h1>🐍 Docgen : Automated Universal Docstring Generator</h1><p>Intelligent Documentation Engine</p></div>', unsafe_allow_html=True)

# ---------- UPLOAD (MODIFIED: Multi-file & ZIP Support) ----------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
# Changed to accept_multiple_files=True and added zip to types
uploaded_files = st.file_uploader(
    "Upload Python (.py) files or a Project ZIP", 
    type=["py", "js", "java", "cpp", "c", "zip"], 
    accept_multiple_files=True
)

col_a, col_b = st.columns(2)
with col_a:
    use_ai = st.toggle("🚀 Enable AI Analysis (Groq/Llama 3.3)", value=True)
with col_b:
    doc_style = st.selectbox("Style Preference", ["google", "numpy", "sphinx"])

st.markdown('</div>', unsafe_allow_html=True)

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["✨ Docstring Generator", "🔍 Code Reviewer", "📄 README Generator"])

# ---------- TAB 1: DOCSTRING GENERATOR ----------
with tab1:
    generate = st.button("✨ Generate Docstrings", key="gen_btn")

    if uploaded_files and generate:
        try:
            combined_original = ""
            combined_updated = ""

            with st.spinner("Processing workspace and generating docstrings..."):
                for uploaded_file in uploaded_files:
                    to_process = []
                    
                    # Check if ZIP
                    if uploaded_file.name.endswith('.zip'):
                        with zipfile.ZipFile(uploaded_file) as z:
                            for file_path in z.namelist():
                                # Only process code files inside ZIP
                                if file_path.endswith(('.py', '.js', '.java', '.cpp', '.c')):
                                    with z.open(file_path) as f:
                                        to_process.append((file_path, f.read().decode("utf-8")))
                    else:
                        # Individual file
                        to_process.append((uploaded_file.name, uploaded_file.read().decode("utf-8")))

                    # Core processing loop for each file
                    for filename, code in to_process:
                        updated_code = code
                        detected_lang = detect_language(code)
                        functions = extract_functions(code, language=detected_lang)
                        
                        if functions:
                            for func_info in functions:
                                if func_info["docstring"]:
                                    continue

                                # Maintain your specific node check logic
                                if func_info.get("node") is None:
                                    func_metadata = analyze_function(func_info)
                                else:
                                    func_metadata = analyze_function(
                                        func_info["node"],
                                        class_name=func_info["class_name"]
                                    )

                                if use_ai:
                                    try:
                                        doc = generate_ai_docstring(func_metadata, style=doc_style, language=detected_lang)
                                        is_ai = True
                                    except Exception as e:
                                        st.error(f"AI failed for {func_info['name']} in {filename}: {e}")
                                        doc = generate_docstring(func_metadata)
                                        is_ai = False
                                else:
                                    doc = generate_docstring(func_metadata)
                                    is_ai = False

                                updated_code = insert_docstring(updated_code, func_metadata, doc)

                        # Append each file to the shared view strings
                        combined_original += f"\n# --- FILE: {filename} ---\n" + code + "\n"
                        combined_updated += f"\n# --- FILE: {filename} ---\n" + updated_code + "\n"

                # Update session state with combined code
                st.session_state.doc_results = combined_updated
                st.session_state.original_code = combined_original
                st.session_state.chat_code = combined_original

        except Exception as e:
            st.error(f"Error processing workspace: {e}")

    # Results view
    if st.session_state.doc_results:
        st.success("✨ Workspace processed successfully!")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📄 Original")
            st.code(st.session_state.original_code)
        with col2:
            st.markdown("### ⚡ Documented")
            st.code(st.session_state.doc_results)

        st.download_button(
            "⬇ Download Result",
            data=st.session_state.doc_results,
            file_name="documented_workspace.txt",
            key="download_btn"
        )

# ---------- TAB 2: CODE REVIEWER ----------
with tab2:
    review_button = st.button("🔍 Review My Code", key="review_btn")

    if uploaded_files and review_button:
        try:
            if st.session_state.original_code:
                with st.spinner("AI is reviewing your workspace..."):
                    review = review_code(st.session_state.original_code)
                    st.session_state.review_results = review
        except Exception as e:
            st.error(f"Review failed: {e}")
    elif review_button and not uploaded_files:
        st.info("⬆️ Please upload files first!")

    if st.session_state.review_results:
        review = st.session_state.review_results
        st.markdown("### 🔍 Code Review Results")
        for category in ["bugs", "security", "performance", "best_practices"]:
            st.markdown(f"#### {category.replace('_', ' ').title()}")
            if review.get(category):
                for item in review[category]:
                    with st.expander(f"📍 Line {item.get('line', '?')} — {item.get('issue', 'Issue')}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**❌ Problematic Code:**")
                            st.code(item.get("code", ""), language="python")
                        with c2:
                            st.markdown("**✅ Fixed Code:**")
                            st.code(item.get("fix", ""), language="python")
            else:
                st.success(f"No {category} issues found!")

# ---------- TAB 3: README GENERATOR ----------
with tab3:
    readme_button = st.button("📄 Generate README", key="readme_btn")

    if uploaded_files and readme_button:
        try:
            if st.session_state.original_code:
                with st.spinner("AI is generating your README..."):
                    # Using first filename as a project reference
                    readme = generate_readme(st.session_state.original_code, "Workspace")
                    st.session_state.readme_result = readme
        except Exception as e:
            st.error(f"README generation failed: {e}")
    elif readme_button and not uploaded_files:
        st.info("⬆️ Please upload a code file first!")

    if st.session_state.readme_result:
        st.success("✅ README generated successfully!")
        st.code(st.session_state.readme_result, language="markdown")
        st.download_button(
            "⬇ Download README.md",
            data=st.session_state.readme_result,
            file_name="README.md",
            key="readme_download"
        )            

# ---------- SIDEBAR CHAT  ----------
with st.sidebar:
    st.markdown("## Code Chat")
    st.markdown("Ask anything about your uploaded code!")

    if st.session_state.chat_code:
        st.success("✅ Code loaded!")
    if st.session_state.doc_results:
        st.success("✅ Docstrings loaded!")
    if st.session_state.review_results:
        st.success("✅ Review loaded!")

    if not st.session_state.chat_code:
        st.info("⬆️ Upload and generate docstrings first!")
    else:
        st.markdown("---")
        for msg in st.session_state.chat_messages:
            color = "#004d00" if msg["role"] == "user" else "#003366"
            label = "🧑 <b>You</b>" if msg["role"] == "user" else "🤖 <b>AI</b>"
            st.markdown(f"""
            <div style="background-color: {color}; border-radius: 16px; padding: 10px; margin: 6px 0px;">
            {label}<br>{msg['content']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        input_key = f"chat_input_{len(st.session_state.chat_messages)}"
        user_input = st.text_input("Ask about your code:", key=input_key, placeholder="e.g. What does this code do?")

        col_send, col_clear = st.columns([3, 1])
        with col_send:
            send = st.button("Send ", key="send_btn", use_container_width=True)
        with col_clear:
            if st.button("🗑️", key="clear_inline", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

        if send and user_input.strip():
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            try:
                with st.spinner("Thinking..."):
                    response = chat_with_code(
                        messages=st.session_state.chat_messages,
                        code=st.session_state.chat_code,
                        doc_results=st.session_state.doc_results,
                        review_results=st.session_state.review_results
                    )
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception as e:
                st.error(f"Chat failed: {e}")