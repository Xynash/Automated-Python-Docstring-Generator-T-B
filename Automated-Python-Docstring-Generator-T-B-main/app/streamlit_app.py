import sys
import os
import streamlit as st

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

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Docstring Generator",
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

st.markdown('<div class="hero"><h1>🐍 AI Docstring Generator</h1><p>Intelligent Python Documentation Engine</p></div>', unsafe_allow_html=True)

# ---------- UPLOAD ----------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a Python (.py) file", type=["py", "js", "java", "cpp", "c"])

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
                        if func_info["docstring"]:
                            continue

                        func_metadata = analyze_function(
                            func_info["node"],
                            class_name=func_info["class_name"]
                        )

                        if use_ai:
                            try:
                                doc = generate_ai_docstring(func_metadata, style=doc_style)
                                is_ai = True
                            except Exception as e:
                                st.error(f"AI failed for {func_info['name']}: {e}")
                                doc = generate_docstring(func_metadata)
                                is_ai = False
                        else:
                            doc = generate_docstring(func_metadata)
                            is_ai = False

                        updated_code = insert_docstring(updated_code, func_metadata, doc)

                    # Save to session state
                    st.session_state.doc_results = updated_code
                    st.session_state.original_code = code
                    st.session_state.chat_code = code
        except Exception as e:
            st.error(f"Error: {e}")

    # Always show if results exist
    if st.session_state.doc_results:
        mode_text = "AI Mode" if use_ai else "Local Heuristic Mode"
        st.success(f"✨ Docstrings generated successfully using {mode_text}!")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📄 Original")
            st.code(st.session_state.original_code, language="python")
        with col2:
            st.markdown("### ⚡ Documented")
            st.code(st.session_state.doc_results, language="python")

        st.download_button(
            "⬇ Download File",
            data=st.session_state.doc_results,
            file_name=f"doc_{uploaded_file.name}" if uploaded_file else "documented.py",
            key="download_btn"
        )

# ---------- TAB 2: CODE REVIEWER ----------
with tab2:
    review_button = st.button("🔍 Review My Code", key="review_btn")

    if uploaded_file and review_button:
        try:
            code = uploaded_file.read().decode("utf-8")
            with st.spinner("AI is reviewing your code..."):
                review = review_code(code)
                st.session_state.review_results = review
        except Exception as e:
            st.error(f"Review failed: {e}")

    elif review_button and not uploaded_file:
        st.info("⬆️ Please upload a Python file first!")

    # Always show if results exist
    if st.session_state.review_results:
        review = st.session_state.review_results
        st.markdown("### 🔍 Code Review Results")

        st.markdown("#### 🐛 Bugs")
        if review["bugs"]:
            for item in review["bugs"]:
                with st.expander(f"📍 Line {item['line']} — {item['issue']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**❌ Problematic Code:**")
                        st.code(item["code"], language="python")
                    with col_b:
                        st.markdown("**✅ Fixed Code:**")
                        st.code(item["fix"], language="python")
        else:
            st.success("✅ No bugs found!")

        st.markdown("#### 🔒 Security Issues")
        if review["security"]:
            for item in review["security"]:
                with st.expander(f"📍 Line {item['line']} — {item['issue']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**❌ Problematic Code:**")
                        st.code(item["code"], language="python")
                    with col_b:
                        st.markdown("**✅ Fixed Code:**")
                        st.code(item["fix"], language="python")
        else:
            st.success("✅ No security issues found!")

        st.markdown("#### ⚡ Performance")
        if review["performance"]:
            for item in review["performance"]:
                with st.expander(f"📍 Line {item['line']} — {item['issue']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**❌ Problematic Code:**")
                        st.code(item["code"], language="python")
                    with col_b:
                        st.markdown("**✅ Fixed Code:**")
                        st.code(item["fix"], language="python")
        else:
            st.success("✅ No performance issues found!")

        st.markdown("#### ✅ Best Practices")
        if review["best_practices"]:
            for item in review["best_practices"]:
                with st.expander(f"📍 Line {item['line']} — {item['issue']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**❌ Problematic Code:**")
                        st.code(item["code"], language="python")
                    with col_b:
                        st.markdown("**✅ Fixed Code:**")
                        st.code(item["fix"], language="python")
        else:
            st.success("✅ No best practice issues found!")

# ---------- TAB 3: README GENERATOR ----------
with tab3:
    readme_button = st.button("📄 Generate README", key="readme_btn")

    if uploaded_file and readme_button:
        try:
            code = uploaded_file.read().decode("utf-8")
            with st.spinner("AI is generating your README..."):
                readme = generate_readme(code, uploaded_file.name)
                st.session_state.readme_result = readme
        except Exception as e:
            st.error(f"README generation failed: {e}")

    elif readme_button and not uploaded_file:
        st.info("⬆️ Please upload a code file first!")

    if st.session_state.readme_result:
        st.success("✅ README generated successfully!")

        st.markdown("### 📝 README.md")
        st.code(st.session_state.readme_result, language="markdown")

        st.download_button(
            "⬇ Download README.md",
            data=st.session_state.readme_result,
            file_name="README.md",
            mime="text/markdown",
            key="readme_download"
        )            

# ---------- SIDEBAR CHAT ----------
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

        # Chat history
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
<div style="background-color: #004d00; border-radius: 16px 16px 0px 16px;
padding: 10px 14px; margin: 6px 0px 6px 30px;
color: #ffffff; font-size: 14px;">
🧑 <b>You</b><br>{msg['content']}
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div style="background-color: #003366; border-radius: 16px 16px 16px 0px;
padding: 10px 14px; margin: 6px 30px 6px 0px;
color: #ffffff; font-size: 14px;">
🤖 <b>AI</b><br>{msg['content']}
</div>
""", unsafe_allow_html=True)

        st.markdown("---")

        # Input clears after send using dynamic key
        input_key = f"chat_input_{len(st.session_state.chat_messages)}"
        user_input = st.text_input(
            "Ask about your code:",
            key=input_key,
            placeholder="e.g. What does this code do?"
        )

        col_send, col_clear = st.columns([3, 1])
        with col_send:
            send = st.button("Send ", key="send_btn", use_container_width=True)
        with col_clear:
            if st.button("🗑️", key="clear_inline", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

        if send:
            if user_input.strip():
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": user_input
                })
                try:
                    with st.spinner("Thinking..."):
                        response = chat_with_code(
                            messages=st.session_state.chat_messages,
                            code=st.session_state.chat_code,
                            doc_results=st.session_state.doc_results,
                            review_results=st.session_state.review_results
                        )
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Chat failed: {e}")
            else:
                st.warning("Please type a message first!")