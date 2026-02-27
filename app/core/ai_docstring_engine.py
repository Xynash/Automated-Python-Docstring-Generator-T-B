import os
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
        print("✅ DEBUG: Groq Client Initialized.")
    except Exception as e:
        print(f"❌ DEBUG: Groq Init Failed: {e}")

def generate_ai_docstring(func_data, style="google"):
    """
    Generates docstring using AI and cleans it for the AST inserter.
    """
    global client
    if not client:
        raise Exception("AI Client is not initialized.")

    # Pass data and style to the prompt builder
    prompt = build_prompt(func_data, style)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional Python documentation expert. Write a {style}-style docstring. Return ONLY the docstring."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        # Get raw response
        doc = completion.choices[0].message.content.strip()
        
        # --- THE FIX: REMOVE EXTRA QUOTES ---
        # This prevents the '''""" logic and makes it clean
        doc = doc.replace("```python", "").replace("```", "")
        doc = doc.strip().strip('"').strip("'")
        
        return doc

    except Exception as e:
        raise Exception(f"Groq API Error: {str(e)}")