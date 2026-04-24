import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from app.core.prompt_builder import build_prompt

# 1. Load environment variables (Local .env)
load_dotenv()

# 2. Define a global client placeholder
client = None

def get_client():
    """
    Robust client initializer that checks both OS environment (.env)
    and Streamlit Secrets (Cloud).
    """
    global client
    if client is not None:
        return client
    
    # Try local .env / OS env first, then try Streamlit Secrets
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        raise Exception("GROQ_API_KEY not found. Please check your .env file or Streamlit Secrets.")

    try:
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        raise Exception(f"Failed to initialize Groq Client: {e}")

MODEL = "llama-3.3-70b-versatile"

def clean_ai_output(doc: str) -> str:
    """Removes markdown and quotes so the Inserter gets raw text."""
    doc = doc.replace("```python", "").replace("```", "")
    doc = doc.replace('"""', "").replace("'''", "")
    prefixes = ["Here is the docstring:", "Here's the docstring:", "Docstring:", "Result:"]
    for p in prefixes:
        doc = doc.replace(p, "")
    return doc.strip()

def generate_ai_docstring(func_data, style="google", language=None):
    """Generates a professional docstring and cleans it for the inserter."""
    
    # --- Robust Client Check ---
    ai_client = get_client()

    if not language:
        from app.core.prompt_builder import detect_language
        language = detect_language(func_data.get("full_code", ""))

    prompt = build_prompt(func_data, style, language)

    language_map = {
        "python": "Senior Python Developer",
        "java": "Senior Java Developer",
        "javascript": "Senior JavaScript Developer",
        "c": "Senior C Developer",
        "cpp": "Senior C++ Developer"
    }
    role = language_map.get(language, "Senior Software Developer")

    style_label = {
        "java": "Javadoc",
        "javascript": "JSDoc",
        "c": "Doxygen",
        "cpp": "Doxygen"
    }.get(language, style.upper())

    try:
        completion = ai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a {role}. 
Write a detailed {style_label} style docstring that accurately describes what the function ACTUALLY does.
Read the code carefully before writing.
Return ONLY the docstring content — no extra text."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        raw_doc = completion.choices[0].message.content.strip()
        return clean_ai_output(raw_doc)

    except Exception as e:
        raise Exception(f"Groq DocGen Error: {str(e)}")

def generate_structured_review(code: str):
    """TASK: Structured Code Review"""
    ai_client = get_client()

    prompt = f"""
    Review the following Python code for bugs, logic errors, and security vulnerabilities.
    Return ONLY a JSON object with keys: bugs (list), security (list), summary (str).
    CODE:
    {code}
    """

    try:
        completion = ai_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.1
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        raise Exception(f"AI Reviewer Error: {str(e)}")

def generate_project_readme(file_context: str):
    """TASK: Project README Generation"""
    ai_client = get_client()
    prompt = f"Generate a professional README.md for this project based on this code context: {file_context}"
    
    try:
        completion = ai_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"README Generation Failed: {str(e)}"