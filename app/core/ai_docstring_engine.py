import os
from groq import Groq
from dotenv import load_dotenv
from app.core.prompt_builder import build_prompt

# 1. Load environment variables from .env file
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_ai_docstring(func_data, style="Google", language="python"):
    """
    Generates a docstring using Groq LLM.
    """
    prompt = build_prompt(func_data, style=style, language=language)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert code documentation assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3
    )
    
    return response.choices[0].message.content.strip()