import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.core.prompt_builder import build_prompt

# 1. Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

# 2. Initialize Client
client = None
if API_KEY:
    try:
        client = Groq(api_key=API_KEY)
        print("✅ SUCCESS: Groq Client Initialized for Milestone 3.")
    except Exception as e:
        print(f"❌ ERROR: Groq Init Failed: {e}")

MODEL = "llama-3.3-70b-versatile"

def clean_ai_output(doc: str) -> str:
    """Removes markdown and quotes so the Inserter gets raw text."""
    doc = doc.replace("```python", "").replace("```", "")
    doc = doc.replace('"""', "").replace("'''", "")
    # Remove common AI prefixes
    prefixes = ["Here is the docstring:", "Here's the docstring:", "Docstring:", "Result:"]
    for p in prefixes:
        doc = doc.replace(p, "")
    return doc.strip()

def generate_ai_docstring(func_data, style="google", language=None):
    """
    Generates a professional docstring and cleans it for the inserter.
    Supports Python, Java, JavaScript, C and C++.
    """
    global client
    if not client:
        raise Exception("AI Client is not initialized.")

    # Auto detect language from code if not provided
    if not language:
        from app.core.prompt_builder import detect_language
        language = detect_language(func_data.get("full_code", ""))

    prompt = build_prompt(func_data, style, language)

    # Language aware system prompt
    language_map = {
        "python": "Senior Python Developer",
        "java": "Senior Java Developer",
        "javascript": "Senior JavaScript Developer",
        "c": "Senior C Developer",
        "cpp": "Senior C++ Developer"
    }
    role = language_map.get(language, "Senior Software Developer")

    # Style label for non-Python
    style_label = {
        "java": "Javadoc",
        "javascript": "JSDoc",
        "c": "Doxygen",
        "cpp": "Doxygen"
    }.get(language, style.upper())

    try:
        completion = client.chat.completions.create(
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
    """
    TASK: Structured Code Review (Milestone 3 Feature)
    Analyzes code for bugs and security risks. Uses Groq JSON Mode.
    """
    global client
    if not client:
        raise Exception("AI Client not initialized.")

    prompt = f"""
    Review the following Python code for bugs, logic errors, and security vulnerabilities.
    
    You must return a JSON object with this exact structure:
    {{
        "bugs": [
            {{"line": 1, "issue": "Description of bug", "problematic": "old_line", "fix": "new_line"}}
        ],
        "security": [
            {{"line": 1, "issue": "Description of risk"}}
        ],
        "summary": "Overall code quality summary (1-2 sentences)"
    }}

    CODE TO REVIEW:
    {code}
    """

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }, # FORCES AI TO RETURN JSON
            temperature=0.1
        )
        
        # Convert string response to Python Dictionary
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        raise Exception(f"AI Reviewer Error: {str(e)}")

def generate_project_readme(file_context: str):
    """
    TASK: Project README Generation (Planned Feature)
    Generates a professional README.md based on provided file metadata.
    """
    global client
    # This logic will be expanded as Member 2 finishes the Prompt logic
    prompt = f"Generate a professional README.md for this project based on this code context: {file_context}"
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"README Generation Failed: {str(e)}"